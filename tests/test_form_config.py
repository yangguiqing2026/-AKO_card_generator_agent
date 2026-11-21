# ============================================
# Author: AKO_studio
# Agent: AKO_card_generator
# Tests for form <-> config conversion
# ============================================

import os
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.core import form_config  # noqa: E402
from src.core.card_generator import (  # noqa: E402
    build_card,
    render_card,
    validate_card_config,
    write_card,
)


def values_fixture():
    return {
        "id": "AKO_gui_agent",
        "name": "GUI Agent",
        "version": "1.2.3",
        "author": "AKO_studio",
        "created_date": "2026-11-21",
        "status": "active",
        "description": "Created via desktop GUI.",
        "capabilities": "- alpha\nbeta\n\n  gamma  \n-",
        "dependencies": "python>=3.9\npyyaml>=6.0",
        "tags": "gui\ndesktop",
        "interfaces": 'input=config.yaml\noutput="AKO_agent_card.yaml"',
        "health_probe": 'endpoint=/health\nexpected_response=ok\nenabled=false',
        "registry": 'registry_agent=AKO_registry_agent\nregistered=false\nretries=2',
        "log_level": "DEBUG",
        "output_path": "nested/card.yaml",
    }


class TestFormConfig(unittest.TestCase):

    def test_parse_list_strips_bullets_and_blanks(self):
        self.assertEqual(
            form_config.parse_list(values_fixture()["capabilities"]),
            ["alpha", "beta", "gamma"],
        )

    def test_parse_mapping_keeps_value_types(self):
        mapping, bad = form_config.parse_mapping(
            "endpoint=/health\nflag=false\ncount=2\nname=\"quoted value\"\ninvalid-line"
        )
        self.assertEqual(mapping["endpoint"], "/health")
        self.assertIs(mapping["flag"], False)
        self.assertIs(mapping["count"], 2)
        self.assertEqual(mapping["name"], "quoted value")
        self.assertEqual(bad, ["invalid-line"])

    def test_form_to_config_round_trip(self):
        values = values_fixture()
        config = form_config.form_to_config(values)
        self.assertEqual(config["output"], {"path": "nested/card.yaml"})
        self.assertEqual(config["agent"]["id"], "AKO_gui_agent")
        self.assertEqual(config["agent"]["log_level"], "DEBUG")
        self.assertEqual(config["agent"]["registry"]["registered"], False)
        self.assertEqual(config["agent"]["registry"]["retries"], 2)

        restored = form_config.config_to_form(config)
        self.assertEqual(restored["id"], values["id"])
        self.assertEqual(restored["capabilities"], "alpha\nbeta\ngamma")
        self.assertEqual(restored["log_level"], "DEBUG")
        self.assertEqual(restored["output_path"], "nested/card.yaml")

    def test_config_to_form_booleans_are_yaml_round_trippable(self):
        values = values_fixture()
        config = form_config.form_to_config(values)
        restored = form_config.config_to_form(config)
        mapping, bad = form_config.parse_mapping(restored["registry"])
        self.assertEqual(bad, [])
        self.assertEqual(mapping, config["agent"]["registry"])

    def test_write_card_from_form_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = form_config.form_to_config(values_fixture())
            agent = validate_card_config(config)
            card = build_card(agent)
            original_cwd = Path.cwd()
            try:
                os.chdir(tmp)
                target = write_card(card, config)
            finally:
                os.chdir(original_cwd)

            self.assertEqual(target, Path(tmp) / "nested" / "card.yaml")
            text = target.read_text(encoding="utf-8")
            self.assertEqual(yaml.safe_load(text), card)
            self.assertFalse(target.with_name(target.name + ".tmp").exists())

    def test_form_to_config_missing_output_uses_default(self):
        values = values_fixture()
        values["output_path"] = ""
        config = form_config.form_to_config(values)
        self.assertEqual(config["output"]["path"], "AKO_agent_card.yaml")

    def test_gui_preview_pipeline(self):
        values = values_fixture()
        config = form_config.form_to_config(values)
        card = build_card(validate_card_config(config))
        text = render_card(card)
        self.assertIn("# Agent Card for: AKO_gui_agent", text)
        self.assertEqual(yaml.safe_load(text), card)
        self.assertNotIn("log_level", yaml.safe_load(text))


if __name__ == "__main__":
    unittest.main()
