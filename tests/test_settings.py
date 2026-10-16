import json
import tempfile
import unittest
from pathlib import Path

from services.settings import load_settings, save_method_state, load_method_state


class TestSettings(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = Path(self.temp_dir.name) / "nested" / "settings.json"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_missing_file_returns_empty_sections(self):
        self.assertEqual(load_settings(self.path), {"graphical_method": {}, "simplex_method": {}})

    def test_save_creates_parent_and_loads_state(self):
        state = {"sense": "Maximize", "c1": "3", "constraints": []}
        save_method_state(self.path, "graphical_method", state)
        self.assertEqual(load_method_state(self.path, "graphical_method"), state)
        self.assertTrue(self.path.exists())

    def test_saving_one_method_preserves_the_other(self):
        save_method_state(self.path, "graphical_method", {"c1": "3"})
        save_method_state(self.path, "simplex_method", {"objective": ["2", "4"]})
        self.assertEqual(load_method_state(self.path, "graphical_method"), {"c1": "3"})
        self.assertEqual(load_method_state(self.path, "simplex_method"), {"objective": ["2", "4"]})

    def test_legacy_graphical_settings_are_migrated(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_text(json.dumps({"sense": "Minimize", "c1": "1", "c2": "2", "constraints": []}), encoding="utf-8")
        settings = load_settings(self.path)
        self.assertEqual(settings["graphical_method"]["sense"], "Minimize")
        self.assertEqual(settings["graphical_method"]["c1"], "1")
        self.assertEqual(settings["simplex_method"], {})

    def test_invalid_json_raises(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_text("{broken", encoding="utf-8")
        with self.assertRaises(json.JSONDecodeError):
            load_settings(self.path)

    def test_non_object_json_raises(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_text("[]", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "JSON object"):
            load_settings(self.path)

    def test_unknown_section_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unknown settings section"):
            save_method_state(self.path, "unknown", {})

    def test_non_dictionary_method_state_rejected(self):
        save_method_state(self.path, "graphical_method", [])
        with self.assertRaisesRegex(ValueError, "Invalid settings"):
            load_method_state(self.path, "graphical_method")


if __name__ == "__main__":
    unittest.main()
