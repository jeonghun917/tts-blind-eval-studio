from __future__ import annotations

import csv
import hashlib
import io
import json
import random
import re
import zipfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

import streamlit as st


APP_VERSION = "2.0.0-alpha.3"
LABELS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
GROUP_RE = re.compile(r"^(?P<item>.+?)__(?P<candidate>.+)\.wav$", re.IGNORECASE)
ALLOWED_METADATA_NAMES = {"metadata.json", "candidate_metadata.json"}
PROTOCOL_PATH = Path(__file__).resolve().parent / "protocols" / "matcha_scaling_v1.json"
TIE_OPTION = "Tie / no meaningful preference"

st.set_page_config(page_title="TTS Blind Eval Studio", page_icon="🎧", layout="wide")


def _stable_seed(seed_text: str) -> int:
    digest = hashlib.sha256(seed_text.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big")


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


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

    if not protocol["artifact_scope_options"]:
        raise RuntimeError("The bundled research protocol has no artifact-scope options.")

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
            "The ZIP package contains item IDs that are not defined by the versioned protocol. "
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
        "study_id",
        "protocol_version",
        "evaluator_id",
        "item_id",
        "category",
        "primary_or_diagnostic",
        "blind_label",
        *[dimension["key"] for dimension in rating_dimensions],
        "artifact_scope",
        "notes",
        "preferred",
        "tie",
    ]
    writer = csv.DictWriter(buf, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue().encode("utf-8")


def _session_metadata_json(
    *,
    study_id: str,
    evaluator_id: str,
    protocol: dict,
    seed_text: str,
    session_note: str,
    session_started_at: str,
    item_ids: list[str],
    candidate_count: int,
    completion_status: str,
    missing_primary_count: int,
    incomplete_score_rows: int,
    missing_preference_count: int,
):
    payload = {
        "schema": "tts-blind-eval-session-v2-alpha",
        "app_version": APP_VERSION,
        "study_id": study_id,
        "evaluator_id": evaluator_id,
        "protocol_version": protocol["protocol_version"],
        "protocol_status": protocol["status"],
        "blind_seed_sha256": _sha256_text(seed_text),
        "session_started_at_utc": session_started_at,
        "exported_at_utc": datetime.now(timezone.utc).isoformat(),
        "session_note": session_note,
        "item_ids": item_ids,
        "item_count": len(item_ids),
        "candidate_count_per_item": candidate_count,
        "completion_status": completion_status,
        "missing_primary_prompt_count": missing_primary_count,
        "incomplete_score_row_count": incomplete_score_rows,
        "missing_preference_count": missing_preference_count,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")


def _key_json(mapping, seed_text: str, protocol_version: str):
    payload = {
        "schema": "tts-blind-eval-key-v2-alpha",
        "app_version": APP_VERSION,
        "protocol_version": protocol_version,
        "blind_seed_sha256": _sha256_text(seed_text),
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
primary_prompt_ids = {
    row["id"] for row in protocol["prompts"] if row.get("analysis") == "primary"
}

st.title("TTS Blind Eval Studio")
st.caption(
    "A protocol-locked blind listening tool for comparing TTS candidates "
    "without exposing internal candidate filenames before scoring."
)
st.caption(
    f"Protocol: {protocol['protocol_version']} · status: {protocol['status']} · app: {APP_VERSION}"
)
if protocol["status"] != "frozen":
    st.warning(
        "This protocol is not marked `frozen`. Do not treat a session as a formal milestone "
        "evaluation until the protocol status is deliberately frozen."
    )

with st.expander("Frozen rating anchors"):
    for dimension in rating_dimensions:
        st.markdown(f"**{dimension['label']}** — {_anchor_help(dimension)}")

study_id = st.text_input("Study ID", value="matcha-scaling-primary")
evaluator_id = st.text_input("Evaluator ID / alias", value="listener-01")
session_note = st.text_input("Session note (optional)", value="")

with st.expander("Input format", expanded=True):
    st.markdown(
        "Upload **one ZIP file** containing WAVs named `ITEM__CANDIDATE.wav`, for example "
        "`S01__candidate_a.wav` and `S01__candidate_b.wav`. "
        "ITEM must be a prompt ID from the versioned protocol. Internal WAV filenames are parsed "
        "in memory and are not rendered before reveal."
    )

seed_text = st.text_input("Blind randomization seed", value=protocol["protocol_version"])
archive_file = st.file_uploader(
    "Upload one blind-evaluation ZIP package",
    type=["zip"],
    accept_multiple_files=False,
)

if not study_id.strip() or not evaluator_id.strip():
    st.info("Enter a Study ID and Evaluator ID before scoring.")
    st.stop()

if not archive_file:
    st.info("Upload one ZIP package containing at least two candidates per item.")
    st.stop()

archive_bytes = archive_file.getvalue()
grouped, _metadata, package_errors = _parse_zip(archive_bytes)
if not package_errors:
    package_errors = _validate_protocol_items(grouped, prompt_by_id)
if package_errors:
    for error in package_errors:
        st.error(error)
    st.stop()

mapping = _build_mapping(grouped, seed_text)
session_token = hashlib.sha256(archive_bytes + seed_text.encode("utf-8")).hexdigest()[:16]
session_started_key = f"session_started::{session_token}"
if session_started_key not in st.session_state:
    st.session_state[session_started_key] = datetime.now(timezone.utc).isoformat()
session_started_at = st.session_state[session_started_key]

st.success(
    f"Loaded {len(mapping)} protocol item(s), "
    f"{sum(len(v) for v in mapping.values())} WAV files total."
)

results = []
preferences = {}
for item, rows in mapping.items():
    prompt = prompt_by_id[item]
    st.divider()
    st.subheader(f"{item} · {prompt['category']}")
    st.write(prompt["text"])
    st.caption(f"Analysis set: {prompt['analysis']}")

    preference_options = [row["blind_label"] for row in rows]
    if protocol["preference_allows_tie"]:
        preference_options.append(TIE_OPTION)
    preference = st.radio(
        "Preferred candidate",
        options=preference_options,
        index=None,
        horizontal=True,
        key=f"{session_token}::preferred::{item}",
    )
    preferences[item] = preference

    cols = st.columns(min(3, len(rows)))
    for idx, row in enumerate(rows):
        with cols[idx % len(cols)]:
            label = row["blind_label"]
            st.markdown(f"### Candidate {label}")
            st.audio(row["bytes"], format="audio/wav")

            scores = {}
            for dimension in rating_dimensions:
                scores[dimension["key"]] = st.selectbox(
                    dimension["label"],
                    options=[1, 2, 3, 4, 5],
                    index=None,
                    placeholder="Choose 1–5",
                    help=_anchor_help(dimension),
                    key=f"{session_token}::{dimension['key']}::{item}::{label}",
                )

            artifact_scope = st.selectbox(
                "Artifact Scope",
                options=protocol["artifact_scope_options"],
                index=None,
                placeholder="Choose artifact scope",
                key=f"{session_token}::artifact_scope::{item}::{label}",
            )
            notes = st.text_area(
                "Notes",
                key=f"{session_token}::notes::{item}::{label}",
            )
            results.append(
                {
                    "study_id": study_id.strip(),
                    "protocol_version": protocol["protocol_version"],
                    "evaluator_id": evaluator_id.strip(),
                    "item_id": item,
                    "category": prompt["category"],
                    "primary_or_diagnostic": prompt["analysis"],
                    "blind_label": label,
                    **scores,
                    "artifact_scope": artifact_scope,
                    "notes": notes,
                    "preferred": preference == label,
                    "tie": preference == TIE_OPTION,
                }
            )

loaded_item_ids = set(mapping)
missing_primary = primary_prompt_ids - loaded_item_ids
incomplete_rows = [
    row
    for row in results
    if any(row[dimension["key"]] is None for dimension in rating_dimensions)
    or row["artifact_scope"] is None
]
missing_preferences = [item for item, value in preferences.items() if value is None]
complete = not missing_primary and not incomplete_rows and not missing_preferences
completion_status = "complete" if complete else "incomplete"

st.divider()
st.subheader("Completion and export")
if complete:
    st.success("All required primary prompts and loaded trials are fully scored.")
else:
    st.warning(
        "Session is incomplete: "
        f"{len(missing_primary)} required primary prompt(s) missing, "
        f"{len(incomplete_rows)} candidate row(s) missing required scores, "
        f"{len(missing_preferences)} loaded prompt(s) missing preference/tie."
    )

explicit_incomplete_export = False
if not complete:
    explicit_incomplete_export = st.checkbox(
        "Export this session explicitly as INCOMPLETE",
        key=f"{session_token}::allow_incomplete_export",
    )
export_allowed = complete or explicit_incomplete_export

if export_allowed:
    st.download_button(
        "Download blind ratings CSV",
        data=_results_csv(results, rating_dimensions),
        file_name="blind_ratings.csv",
        mime="text/csv",
        use_container_width=True,
    )
    st.download_button(
        "Download session metadata JSON",
        data=_session_metadata_json(
            study_id=study_id.strip(),
            evaluator_id=evaluator_id.strip(),
            protocol=protocol,
            seed_text=seed_text,
            session_note=session_note,
            session_started_at=session_started_at,
            item_ids=list(mapping.keys()),
            candidate_count=len(next(iter(mapping.values()))),
            completion_status=completion_status,
            missing_primary_count=len(missing_primary),
            incomplete_score_rows=len(incomplete_rows),
            missing_preference_count=len(missing_preferences),
        ),
        file_name="session_metadata.json",
        mime="application/json",
        use_container_width=True,
    )
else:
    st.info("Complete the required fields, or explicitly export an incomplete session, before reveal.")

with st.expander("Reveal / export blind key"):
    if not export_allowed:
        st.info("Reveal is locked until the session is complete or explicitly marked incomplete for export.")
    else:
        st.warning("Reveal candidate identity only after finishing the intended blind scoring session.")
        if st.checkbox(
            "I have finished scoring and want to reveal candidate identities",
            key=f"{session_token}::reveal_confirm",
        ):
            revealed = {
                item: {row["blind_label"]: row["candidate"] for row in rows}
                for item, rows in mapping.items()
            }
            st.json(revealed)
            st.download_button(
                "Download reveal key JSON",
                data=_key_json(mapping, seed_text, protocol["protocol_version"]),
                file_name="reveal_key.json",
                mime="application/json",
                use_container_width=True,
            )

st.caption(
    f"App {APP_VERSION}. CPU-only; no model checkpoint, dataset, API key, "
    "or external service is required."
)
