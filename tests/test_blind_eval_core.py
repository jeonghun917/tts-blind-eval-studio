from __future__ import annotations

import ast
import hashlib
import io
import json
import random
import re
import unittest
import wave
import zipfile
from collections import defaultdict
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "app.py"
LABELS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
GROUP_RE = re.compile(r"^(?P<item>.+?)__(?P<candidate>.+)\.wav$", re.IGNORECASE)
ALLOWED_METADATA_NAMES = {"metadata.json", "candidate_metadata.json"}


def load_app_helpers() -> dict:
    """Load selected pure helpers from app.py without importing Streamlit."""
    source = APP_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(APP_PATH))
    wanted = {
        "_stable_seed",
        "_safe_member_path",
        "_parse_zip",
        "_validate_protocol_items",
        "_build_mapping",
        "_presentation_order",
    }
    functions = [
        node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in wanted
    ]
    found = {node.name for node in functions}
    if found != wanted:
        raise AssertionError(f"missing app helpers: {sorted(wanted - found)}")

    module = ast.Module(body=functions, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {
        "hashlib": hashlib,
        "io": io,
        "json": json,
        "random": random,
        "re": re,
        "zipfile": zipfile,
        "defaultdict": defaultdict,
        "PurePosixPath": PurePosixPath,
        "LABELS": LABELS,
        "GROUP_RE": GROUP_RE,
        "ALLOWED_METADATA_NAMES": ALLOWED_METADATA_NAMES,
    }
    exec(compile(module, str(APP_PATH), "exec"), namespace)
    return namespace


def synthetic_wav_bytes(sample_rate: int = 8000, frames: int = 80) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(b"\x00\x00" * frames)
    return buf.getvalue()


def make_zip(entries: list[tuple[str, bytes]]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, payload in entries:
            zf.writestr(name, payload)
    return buf.getvalue()


class BlindEvalCoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ns = load_app_helpers()
        cls.parse_zip = staticmethod(cls.ns["_parse_zip"])
        cls.validate_protocol_items = staticmethod(cls.ns["_validate_protocol_items"])
        cls.build_mapping = staticmethod(cls.ns["_build_mapping"])
        cls.presentation_order = staticmethod(cls.ns["_presentation_order"])
        cls.wav = synthetic_wav_bytes()

    def valid_two_item_zip(self) -> bytes:
        return make_zip(
            [
                ("S01__candidate_a.wav", self.wav),
                ("S01__candidate_b.wav", self.wav),
                ("P01__candidate_a.wav", self.wav),
                ("P01__candidate_b.wav", self.wav),
                ("metadata.json", b'{"study":"fixture"}'),
            ]
        )

    def test_valid_synthetic_zip(self) -> None:
        grouped, metadata, errors = self.parse_zip(self.valid_two_item_zip())
        self.assertEqual(errors, [])
        self.assertEqual(set(grouped), {"S01", "P01"})
        self.assertEqual({r["candidate"] for r in grouped["S01"]}, {"candidate_a", "candidate_b"})
        self.assertEqual(metadata["metadata.json"]["study"], "fixture")

    def test_path_traversal_is_rejected_without_leaking_name(self) -> None:
        secret = "checkpoint500k_secret"
        blob = make_zip(
            [
                (f"../S01__{secret}.wav", self.wav),
                ("S01__candidate_b.wav", self.wav),
            ]
        )
        grouped, _metadata, errors = self.parse_zip(blob)
        self.assertEqual(grouped, {})
        self.assertTrue(any("unsafe path" in e.lower() for e in errors))
        self.assertNotIn(secret, " ".join(errors))

    def test_non_wav_member_is_rejected(self) -> None:
        blob = make_zip(
            [
                ("S01__candidate_a.wav", self.wav),
                ("S01__candidate_b.wav", self.wav),
                ("notes.txt", b"not allowed"),
            ]
        )
        grouped, _metadata, errors = self.parse_zip(blob)
        self.assertEqual(grouped, {})
        self.assertTrue(any("non-WAV" in e for e in errors))

    def test_duplicate_item_candidate_pair_is_rejected(self) -> None:
        blob = make_zip(
            [
                ("a/S01__candidate_a.wav", self.wav),
                ("b/S01__candidate_a.wav", self.wav),
                ("S01__candidate_b.wav", self.wav),
            ]
        )
        grouped, _metadata, errors = self.parse_zip(blob)
        self.assertEqual(grouped, {})
        self.assertTrue(any("duplicate item/candidate" in e for e in errors))

    def test_empty_wav_is_rejected(self) -> None:
        blob = make_zip(
            [
                ("S01__candidate_a.wav", b""),
                ("S01__candidate_b.wav", self.wav),
            ]
        )
        grouped, _metadata, errors = self.parse_zip(blob)
        self.assertEqual(grouped, {})
        self.assertTrue(any("empty WAV" in e for e in errors))

    def test_inconsistent_candidate_membership_is_rejected(self) -> None:
        blob = make_zip(
            [
                ("S01__candidate_a.wav", self.wav),
                ("S01__candidate_b.wav", self.wav),
                ("P01__candidate_a.wav", self.wav),
                ("P01__candidate_c.wav", self.wav),
            ]
        )
        grouped, _metadata, errors = self.parse_zip(blob)
        self.assertEqual(grouped, {})
        self.assertTrue(any("membership is inconsistent" in e for e in errors))

    def test_unknown_protocol_item_is_rejected(self) -> None:
        grouped, _metadata, errors = self.parse_zip(self.valid_two_item_zip())
        self.assertEqual(errors, [])
        protocol = {"S01": {}, "P01": {}}
        self.assertEqual(self.validate_protocol_items(grouped, protocol), [])
        protocol.pop("P01")
        errors = self.validate_protocol_items(grouped, protocol)
        self.assertTrue(any("Unknown item count: 1" in e for e in errors))

    def test_candidate_mapping_is_deterministic(self) -> None:
        grouped, _metadata, errors = self.parse_zip(self.valid_two_item_zip())
        self.assertEqual(errors, [])
        first = self.build_mapping(grouped, "fixture-seed")
        second = self.build_mapping(grouped, "fixture-seed")
        self.assertEqual(
            [(r["candidate"], r["blind_label"]) for r in first["S01"]],
            [(r["candidate"], r["blind_label"]) for r in second["S01"]],
        )

    def test_candidate_mapping_for_item_is_independent_of_other_items(self) -> None:
        grouped, _metadata, errors = self.parse_zip(self.valid_two_item_zip())
        self.assertEqual(errors, [])
        full = self.build_mapping(grouped, "fixture-seed")
        only_s01 = self.build_mapping({"S01": grouped["S01"]}, "fixture-seed")
        self.assertEqual(
            [(r["candidate"], r["blind_label"]) for r in full["S01"]],
            [(r["candidate"], r["blind_label"]) for r in only_s01["S01"]],
        )

    def test_prompt_order_is_deterministic_and_complete(self) -> None:
        grouped, _metadata, errors = self.parse_zip(self.valid_two_item_zip())
        self.assertEqual(errors, [])
        mapping = self.build_mapping(grouped, "fixture-seed")
        first = self.presentation_order(mapping, "fixture-seed")
        second = self.presentation_order(mapping, "fixture-seed")
        self.assertEqual(first, second)
        self.assertEqual(set(first), set(mapping))
        self.assertEqual(len(first), len(mapping))


if __name__ == "__main__":
    unittest.main()
