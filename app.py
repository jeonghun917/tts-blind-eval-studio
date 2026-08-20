from __future__ import annotations

import csv
import hashlib
import io
import json
import random
import re
import zipfile
from collections import defaultdict
from pathlib import PurePosixPath

import streamlit as st


APP_VERSION = "2.0.0-alpha.1"
LABELS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
GROUP_RE = re.compile(r"^(?P<item>.+?)__(?P<candidate>.+)\.wav$", re.IGNORECASE)
ALLOWED_METADATA_NAMES = {"metadata.json", "candidate_metadata.json"}

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
                except (UnicodeDecodeError, json.JSONDecodeError):
                    errors.append("A metadata JSON file is not valid UTF-8 JSON.")
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

            data = archive.read(info)
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


def _results_csv(rows):
    buf = io.StringIO()
    fields = [
        "item",
        "blind_label",
        "rating_1_5",
        "artifact_1_5",
        "naturalness_1_5",
        "notes",
        "preferred",
    ]
    writer = csv.DictWriter(buf, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue().encode("utf-8")


def _key_json(mapping, seed_text: str):
    payload = {
        "schema": "tts-blind-eval-key-v2-alpha",
        "app_version": APP_VERSION,
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


st.title("TTS Blind Eval Studio")
st.caption(
    "A small, model-agnostic blind listening tool for comparing TTS candidates "
    "without exposing internal candidate filenames before scoring."
)

with st.expander("Input format", expanded=True):
    st.markdown(
        "Upload **one ZIP file** containing WAVs named `ITEM__CANDIDATE.wav`, for example "
        "`S01__candidate_a.wav` and `S01__candidate_b.wav`. "
        "Internal WAV filenames are parsed in memory and are not rendered before reveal."
    )

seed_text = st.text_input("Blind randomization seed", value="matcha-scaling-v1")
archive_file = st.file_uploader(
    "Upload one blind-evaluation ZIP package",
    type=["zip"],
    accept_multiple_files=False,
)

if not archive_file:
    st.info("Upload one ZIP package containing at least two candidates per item.")
    st.stop()

grouped, _metadata, package_errors = _parse_zip(archive_file.getvalue())
if package_errors:
    for error in package_errors:
        st.error(error)
    st.stop()

mapping = _build_mapping(grouped, seed_text)

st.success(
    f"Loaded {len(mapping)} blind comparison item(s), "
    f"{sum(len(v) for v in mapping.values())} WAV files total."
)

results = []
for item, rows in mapping.items():
    st.divider()
    st.subheader(item)
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
            overall = st.slider("Overall", 1, 5, 3, key=f"overall::{item}::{label}")
            natural = st.slider("Naturalness", 1, 5, 3, key=f"natural::{item}::{label}")
            artifact = st.slider(
                "Artifact severity (1=none, 5=severe)",
                1,
                5,
                3,
                key=f"artifact::{item}::{label}",
            )
            notes = st.text_area("Notes", key=f"notes::{item}::{label}")
            results.append(
                {
                    "item": item,
                    "blind_label": label,
                    "rating_1_5": overall,
                    "artifact_1_5": artifact,
                    "naturalness_1_5": natural,
                    "notes": notes,
                    "preferred": label == preferred,
                }
            )

st.divider()
st.subheader("Export")
st.download_button(
    "Download blind ratings CSV",
    data=_results_csv(results),
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
            data=_key_json(mapping, seed_text),
            file_name="tts_blind_eval_key.json",
            mime="application/json",
            use_container_width=True,
        )

st.caption(
    f"App {APP_VERSION}. CPU-only; no model checkpoint, dataset, API key, "
    "or external service is required."
)
