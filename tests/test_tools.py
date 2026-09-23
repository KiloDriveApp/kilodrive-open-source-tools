from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from kd_devtools import contractforge, docstruth, schemacert, storeframe  # noqa: E402


class StoreFrameTests(unittest.TestCase):
    def test_generates_opaque_image_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            Image.new("RGB", (120, 240), "white").save(root / "screen.png")
            config = {
                "canvas": [300, 600],
                "output": "output",
                "brand": "Example",
                "colors": {"top": "#D8FFE1", "bottom": "#1689D9", "text": "#082D35"},
                "frame": {"width": 220, "height": 380, "top": 180, "border": 8},
                "slides": [{"source": "screen.png", "title": "A useful screen", "slug": "useful"}],
            }
            config_path = root / "config.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            outputs = storeframe.generate(config_path)
            self.assertEqual(len(outputs), 1)
            with Image.open(outputs[0]) as generated:
                self.assertEqual(generated.size, (300, 600))
                self.assertEqual(generated.mode, "RGB")
            manifest = json.loads((root / "output/manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(len(manifest["assets"][0]["sha256"]), 64)


class ContractForgeTests(unittest.TestCase):
    def test_generates_required_and_nullable_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "openapi.json"
            source.write_text(json.dumps({"components": {"schemas": {"Thing": {
                "type": "object", "required": ["id"],
                "properties": {"id": {"type": "integer"}, "label": {"type": "string"}}
            }}}}), encoding="utf-8")
            output = root / "models.dart"
            contractforge.generate(source, output)
            value = output.read_text(encoding="utf-8")
            self.assertIn("final int id;", value)
            self.assertIn("final String? label;", value)
            self.assertIn("required this.id", value)


class DocsTruthTests(unittest.TestCase):
    def test_reports_broken_links_and_banned_claims(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "README.md").write_text("[missing](missing.md) guaranteed secure", encoding="utf-8")
            config = root / "config.json"
            config.write_text(json.dumps({"include": ["*.md"], "bannedPhrases": ["guaranteed secure"]}), encoding="utf-8")
            errors = docstruth.validate(config)
            self.assertEqual(len(errors), 2)


class SchemaCertTests(unittest.TestCase):
    def test_rejects_unsafe_prefix_before_process_execution(self) -> None:
        os.environ["UNIT_TEST_MYSQL_PASSWORD"] = "synthetic"
        with self.assertRaises(ValueError):
            schemacert.certify(mysql="mysql", host="localhost", port=3306, user="root",
                               password_env="UNIT_TEST_MYSQL_PASSWORD", scripts=[], checks=[], prefix="bad-name;drop")


if __name__ == "__main__":
    unittest.main()
