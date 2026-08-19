from __future__ import annotations

import csv
import hashlib
import io
import json
import random
import re
from collections import defaultdict

import streamlit as st


st.set_page_config(page_title="TTS Blind Eval Studio", page_icon="🎧", layout="wide")

LABELS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
GROUP_RE = re.compile(r"^(?P<item>.+?)__(?P<candidate>.+)\.wav$", re.IGNORECASE)


def _stable_seed(seed_text: str) -> int:
    digest = hashlib.sha256(seed_text.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big")


def _parse_uploads(files):
    grouped = defaultdict(list)
    errors = []
    for f in files:
        m = GROUP_RE.match(f.name)
        if not m:
            errors.append(f.name)
            continue
        grouped[m.group("item")].append(
            {
                "candidate": m.group("candidate"),
                "name": f.name,
                "bytes": f.getvalue(),
            }
        )
    return dict(sorted(grouped.items())), errors


def _build_mapping(grouped, seed_text: str):
    rng = random.Random(_stable_seed(seed_text))
    mapping = {}
    for item, candidates in grouped.items():
        if len(candidates) > len(LABELS):
            raise ValueError(f"{item}: too many candidates ({len(candidates)})")
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
        "schema": "tts-blind-eval-key-v1",
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
st.caption("A small, model-agnostic blind listening tool for comparing TTS candidates without exposing model names during scoring.")

with st.expander("Input format", expanded=True):
    st.markdown(
        "Upload WAV files named `ITEM__CANDIDATE.wav`, for example "
        "`sentence01__baseline.wav`, `sentence01__checkpoint500k.wav`, "
        "`sentence01__reference.wav`. Files sharing the same ITEM are compared together."
    )

seed_text = st.text_input("Blind randomization seed", value="lightning-demo-v1")
files = st.file_uploader("Upload WAV candidates", type=["wav"], accept_multiple_files=True)

if not files:
    st.info("Upload at least two WAV files to begin.")
    st.stop()

grouped, bad_names = _parse_uploads(files)
if bad_names:
    st.error("These files do not match ITEM__CANDIDATE.wav: " + ", ".join(bad_names))
    st.stop()

invalid = [item for item, rows in grouped.items() if len(rows) < 2]
if invalid:
    st.error("Each item needs at least two candidates: " + ", ".join(invalid))
    st.stop()

mapping = _build_mapping(grouped, seed_text)

st.success(f"Loaded {len(mapping)} blind comparison item(s), {sum(len(v) for v in mapping.values())} WAV files total.")

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

st.caption("The app is model-agnostic and does not require a GPU, model checkpoint, dataset, API key, or external service.")
