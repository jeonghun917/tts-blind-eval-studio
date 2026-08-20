from __future__ import annotations

import csv
import hashlib
import io
import json
import random
import re
import zipfile
from collections import defaultdict
from pathlib import Path, PurePosixPath

import streamlit as st


APP_VERSION = "2.0.0-alpha.2"
LABELS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
GROUP_RE = re.compile(r"^(?P<item>.+?)__(?P<candidate>.+)\.wav$", re.IGNORECASE)
ALLOWED_METADATA_NAMES = {"metadata.json", "candidate_metadata.json"}
PROTOCOL_PATH = Path(__file__).resolve().parent / "protocols" / "matcha_scaling_v1.json"

st.set_page_config(page_title="TTS Blind Eval Studio", page_icon="🎧", layout="wide")


def _stable_seed(seed_text: str) -> int:
    digest = hashlib.sha256(seed_text.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big")


def _safe_member_path(name: str) -> bool:
    normalized = name.replace("\\", "/")
    path = PurePosixPath(normalized)
    if path.is_absolute():
        return False
    return bool(path.parts) and all(part not in {"", ".", ".."} for part in path.parts)


def _load_protocol() -> dict:
    try:
        protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("The bundled research protocol could not be loaded.") from exc

    required_top_level = {
        "protocol_version",
        "status",
        "prompts",
        "rating_dimensions",
        "artifact_scope_options",
        "preference_allows_tie",
    }
    if not required_top_level.issubset(protocol):
        raise RuntimeError("The bundled research protocol is missing required fields.")

    prompt_ids = [row.get("id") for row in protocol["prompts"]]
    if not prompt_ids or any(not value for value in prompt_ids) or len(prompt_ids) != len(set(prompt_ids)):
        raise RuntimeError("The bundled research protocol has invalid or duplicate prompt IDs.")

    dimension_keys = [row.get("key") for row in protocol["rating_dimensions"]]
    if not dimension_keys or any(not value for value in dimension_keys) or len(dimension_keys) != len(set(dimension_keys)):
        raise RuntimeError("The bundled research protocol has invalid or duplicate rating dimensions.")

    return protocol


def _parse_zip(blob: bytes):
    grouped = defaultdict(list)
    seen_pairs = set()
    invalid_wav_names = 0
    metadata_files = {}
    errors = []

    try:
        archive = zipfile.ZipFile(io.BytesIO(blob))
    except (zipfile.BadZipFile, OSError):
        return {}, {}, ["The uploaded file is not a valid ZIP archive."]

    with archive:
        members = [info for info in archive.infolist() if not info.is_dir()]
        if not members:
            return {}, {}, ["The ZIP archive is empty."]

        seen_member_names = set()
        for info in members:
            internal_name = info.filename.replace("\\", "/")
            if internal_name in seen_member_names:
                errors.append("The ZIP archive contains duplicate member names.")
                continue
            seen_member_names.add(internal_name)

            if not _safe_member_path(internal_name):
                errors.append("The ZIP archive contains an unsafe path.")
                continue

            base_name = PurePosixPath(internal_name).name
            lower_base = base_name.lower()

            if lower_base.endswith(".json"):
                if lower_base not in ALLOWED_METADATA_NAMES:
                    errors.append("The ZIP archive contains an unsupported JSON metadata file.")
                    continue
                if lower_base in metadata_files:
                    errors.append("The ZIP archive contains duplicate metadata files.")
                    continue
                try:
                    metadata_files[lower_base] = json.loads(archive.read(info).decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError, zipfile.BadZipFile, RuntimeError, OSError):
                    errors.append("A metadata JSON file could not be read as valid UTF-8 JSON.")
                continue

            if not lower_base.endswith(".wav"):
                errors.append("The ZIP archive contains a non-WAV file.")
                continue

            match = GROUP_RE.match(base_name)
            if not match:
                invalid_wav_names += 1
                continue

            item = match.group("item")
            candidate = match.group("candidate")
            pair = (item, candidate)
            if pair in seen_pairs:
                errors.append("The ZIP archive contains a duplicate item/candidate pair.")
                continue
            seen_pairs.add(pair)

            try:
                data = archive.read(info)
            except (zipfile.BadZipFile, RuntimeError, OSError):
                errors.append("A WAV member in the ZIP archive could not be read.")
                continue
            if not data:
                errors.append("The ZIP archive contains an empty WAV file.")
                continue

            grouped[item].append(
                {
                    "candidate": candidate,
                    "name": internal_name,
                    "bytes": data,
                }
            )

    if invalid_wav_names:
        errors.append(
            f"{invalid_wav_names} WAV file(s) do not follow the required ITEM__CANDIDATE.wav convention."
        )

    if errors:
        return {}, metadata_files, errors

    grouped = dict(sorted(grouped.items()))
    if not grouped:
        return {}, metadata_files, ["The ZIP archive contains no valid WAV candidates."]

    invalid_counts = [item for item, rows in grouped.items() if len(rows) < 2]
    if invalid_counts:
        return {}, metadata_files, [
            "Every item must contain at least two candidates. "
            f"Invalid item count: {len(invalid_counts)}."
        ]

    too_many = [item for item, rows in grouped.items() if len(rows) > len(LABELS)]
    if too_many:
        return {}, metadata_files, [
            f"An item exceeds the supported maximum of {len(LABELS)} candidates."
        ]

    candidate_sets = {item: {row["candidate"] for row in rows} for item, rows in grouped.items()}
    expected = next(iter(candidate_sets.values()))
    inconsistent = [item for item, values in candidate_sets.items() if values != expected]
    if inconsistent:
        return {}, metadata_files, [
            "Candidate membership is inconsistent across items. "
            f"Affected item count: {len(inconsistent)}."
        ]

    return grouped, metadata_files, []


def _validate_protocol_items(grouped: dict, prompt_by_id: dict) -> list[str]:
    unknown = [item for item in grouped if item not in prompt_by_id]
    if unknown:
        return [
            "The ZIP package contains item IDs that are not defined by the frozen protocol. "
            f"Unknown item count: {len(unknown)}."
        ]
    return []


def _build_mapping(grouped, seed_text: str):
    rng = random.Random(_stable_seed(seed_text))
    mapping = {}
    for item, candidates in grouped.items():
        shuffled = list(candidates)
        rng.shuffle(shuffled)
        mapping[item] = [
            {**candidate, "blind_label": LABELS[i]}
            for i, candidate in enumerate(shuffled)
        ]
    return mapping


def _anchor_help(dimension: dict) -> str:
    anchors = dimension.get("anchors", {})
    parts = []
    for key in ("1", "3", "5"):
        if key in anchors:
            parts.append(f"{key}: {anchors[key]}")
    return " | ".join(parts)


def _results_csv(rows, rating_dimensions):
    buf = io.StringIO()
    fields = [
        "item",
        "category",
        "primary_or_diagnostic",
        "blind_label",
        *[dimension["key"] for dimension in rating_dimensions],
        "notes",
        "preferred",
    ]
    writer = csv.DictWriter(buf, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue().encode("utf-8")


def _key_json(mapping, seed_text: str, protocol_version: str):
    payload = {
        "schema": "tts-blind-eval-key-v2-alpha",
        "app_version": APP_VERSION,
        "protocol_version": protocol_version,
        "seed": seed_text,
        "items": {
            item: {
                row["blind_label"]: {
                    "candidate": row["candidate"],
                    "source_filename": row["name"],
                }
                for row in rows
            }
            for item, rows in mapping.items()
        },
    }
    return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")


try:
    protocol = _load_protocol()
except RuntimeError as exc:
    st.error(str(exc))
    st.stop()

prompt_by_id = {row["id"]: row for row in protocol["prompts"]}
rating_dimensions = protocol["rating_dimensions"]

st.title("TTS Blind Eval Studio")
st.caption(
    "A protocol-locked blind listening tool for comparing TTS candidates "
    "without exposing internal candidate filenames before scoring."
)
st.caption(
    f"Protocol: {protocol['protocol_version']} · status: {protocol['status']} · app: {APP_VERSION}"
)

with st.expander("Frozen rating anchors"):
    for dimension in rating_dimensions:
        st.markdown(f"**{dimension['label']}** — {_anchor_help(dimension)}")

with st.expander("Input format", expanded=True):
    st.markdown(
        "Upload **one ZIP file** containing WAVs named `ITEM__CANDIDATE.wav`, for example "
        "`S01__candidate_a.wav` and `S01__candidate_b.wav`. "
        "ITEM must be a prompt ID from the frozen protocol. Internal WAV filenames are parsed "
        "in memory and are not rendered before reveal."
    )

seed_text = st.text_input("Blind randomization seed", value=protocol["protocol_version"])
archive_file = st.file_uploader(
    "Upload one blind-evaluation ZIP package",
    type=["zip"],
    accept_multiple_files=False,
)

if not archive_file:
    st.info("Upload one ZIP package containing at least two candidates per item.")
    st.stop()

grouped, _metadata, package_errors = _parse_zip(archive_file.getvalue())
if not package_errors:
    package_errors = _validate_protocol_items(grouped, prompt_by_id)
if package_errors:
    for error in package_errors:
        st.error(error)
    st.stop()

mapping = _build_mapping(grouped, seed_text)

st.success(
    f"Loaded {len(mapping)} protocol item(s), "
    f"{sum(len(v) for v in mapping.values())} WAV files total."
)

results = []
for item, rows in mapping.items():
    prompt = prompt_by_id[item]
    st.divider()
    st.subheader(f"{item} · {prompt['category']}")
    st.write(prompt["text"])
    st.caption(f"Analysis set: {prompt['analysis']}")

    preferred = st.radio(
        "Preferred candidate",
        options=[row["blind_label"] for row in rows],
        horizontal=True,
        key=f"preferred::{item}",
    )
    cols = st.columns(min(3, len(rows)))
    for idx, row in enumerate(rows):
        with cols[idx % len(cols)]:
            label = row["blind_label"]
            st.markdown(f"### Candidate {label}")
            st.audio(row["bytes"], format="audio/wav")

            scores = {}
            for dimension in rating_dimensions:
                scores[dimension["key"]] = st.slider(
                    dimension["label"],
                    1,
                    5,
                    3,
                    help=_anchor_help(dimension),
                    key=f"{dimension['key']}::{item}::{label}",
                )

            notes = st.text_area("Notes", key=f"notes::{item}::{label}")
            results.append(
                {
                    "item": item,
                    "category": prompt["category"],
                    "primary_or_diagnostic": prompt["analysis"],
                    "blind_label": label,
                    **scores,
                    "notes": notes,
                    "preferred": label == preferred,
                }
            )

st.divider()
st.subheader("Export")
st.download_button(
    "Download blind ratings CSV",
    data=_results_csv(results, rating_dimensions),
    file_name="tts_blind_eval_results.csv",
    mime="text/csv",
    use_container_width=True,
)

with st.expander("Reveal / export blind key"):
    st.warning("Open this only after scoring if you want to preserve the blind evaluation.")
    if st.checkbox("I have finished scoring and want to reveal the mapping"):
        revealed = {
            item: {row["blind_label"]: row["candidate"] for row in rows}
            for item, rows in mapping.items()
        }
        st.json(revealed)
        st.download_button(
            "Download blind key JSON",
            data=_key_json(mapping, seed_text, protocol["protocol_version"]),
            file_name="tts_blind_eval_key.json",
            mime="application/json",
            use_container_width=True,
        )

st.caption(
    f"App {APP_VERSION}. CPU-only; no model checkpoint, dataset, API key, "
    "or external service is required."
)
