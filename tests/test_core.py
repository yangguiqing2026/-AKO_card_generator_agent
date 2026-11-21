# ============================================
# Author: AKO_studio
# Agent: AKO_card_generator
# Tests for: Ako Card Generator
# ============================================

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.core.card_generator import (  # noqa: E402
    build_card,
    generate_card,
    load_config,
    render_card,
    validate_card_config,
)


def sample_agent():
    return {
        "id": "AKO_test_agent",
        "name": "Test Agent",
        "version": "0.1.0",
        "author": "AKO_studio",
        "created_date": "2026-11-21",
        "status": "active",
        "description": "Test agent for unit tests.",
        "capabilities": ["testing"],
        "dependencies": ["python>=3.9"],
        "interfaces": {"input": "yaml"},
        "health_probe": {"endpoint": "/health"},
        "registry": {"registered": False},
        "tags": ["test"],
        "log_level": "INFO",
    }


def write_config(directory, agent=None, output_path="card.yaml"):
    config = {
        "agent": agent if agent is not None else sample_agent(),
        "output": {"path": output_path},
    }
    config_path = Path(directory) / "config.yaml"
    config_path.write_text(
        yaml.safe_dump(config, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    return config_path


class TestCardGenerator(unittest.TestCase):

    def test_load_config_returns_mapping(self):
        with tempfile.TemporaryDirectory() as tmp:
            config_path = write_config(tmp)
            config = load_config(config_path)
            self.assertEqual(config["agent"]["id"], "AKO_test_agent")
            self.assertEqual(config["output"]["path"], "card.yaml")

    def test_load_config_missing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                load_config(Path(tmp) / "missing.yaml")

    def test_validate_rejects_missing_required_field(self):
        agent = sample_agent()
        agent.pop("version")
        with self.assertRaisesRegex(ValueError, "agent.version"):
            validate_card_config({"agent": agent})

    def test_validate_rejects_wrong_list_type(self):
        agent = sample_agent()
        agent["capabilities"] = "not-a-list"
        with self.assertRaisesRegex(ValueError, "agent.capabilities"):
            validate_card_config({"agent": agent})

    def test_validate_rejects_wrong_dict_type(self):
        agent = sample_agent()
        agent["interfaces"] = ["not-a-dict"]
        with self.assertRaisesRegex(ValueError, "agent.interfaces"):
            validate_card_config({"agent": agent})

    def test_build_card_maps_id_and_excludes_log_level(self):
        card = build_card(sample_agent())
        self.assertEqual(card["agent_id"], "AKO_test_agent")
        self.assertNotIn("id", card)
        self.assertNotIn("log_level", card)
        self.assertEqual(
            list(card.keys()),
            [
                "agent_id",
                "name",
                "version",
                "author",
                "created_date",
                "status",
                "description",
                "capabilities",
                "dependencies",
                "interfaces",
                "health_probe",
                "registry",
                "tags",
            ],
        )

    def test_generate_card_writes_valid_yaml(self):
        with tempfile.TemporaryDirectory() as tmp:
            config_path = write_config(tmp, output_path="out/card.yaml")
            original_cwd = Path.cwd()
            try:
                os.chdir(tmp)
                target, card = generate_card(config_path)
            finally:
                os.chdir(original_cwd)

            self.assertEqual(target, Path(tmp) / "out" / "card.yaml")
            self.assertTrue(target.is_file())
            self.assertFalse(target.with_name(target.name + ".tmp").exists())

            text = target.read_text(encoding="utf-8")
            self.assertIn("# Agent Card for: AKO_test_agent", text)
            self.assertEqual(yaml.safe_load(text), card)

    def test_render_card_is_deterministic(self):
        card = build_card(sample_agent())
        self.assertEqual(render_card(card), render_card(card))

    def test_cli_end_to_end(self):
        with tempfile.TemporaryDirectory() as tmp:
            config_path = write_config(tmp, output_path="from-config.yaml")
            output_path = Path(tmp) / "cli-card.yaml"

            result = subprocess.run(
                [
                    sys.executable,
                    str(PROJECT_ROOT / "src" / "core" / "main.py"),
                    "--config",
                    str(config_path),
                    "--output",
                    str(output_path),
                ],
                cwd=tmp,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(output_path.is_file())
            self.assertEqual(
                yaml.safe_load(output_path.read_text(encoding="utf-8"))["agent_id"],
                "AKO_test_agent",
            )

    def test_cli_invalid_config_returns_nonzero(self):
        with tempfile.TemporaryDirectory() as tmp:
            agent = sample_agent()
            agent.pop("description")
            config_path = write_config(tmp, agent=agent, output_path="bad.yaml")
            output_path = Path(tmp) / "bad.yaml"

            result = subprocess.run(
                [
                    sys.executable,
                    str(PROJECT_ROOT / "src" / "core" / "main.py"),
                    "--config",
                    str(config_path),
                ],
                cwd=tmp,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 1)
            self.assertFalse(output_path.exists())
            self.assertIn("agent.description", result.stderr)


if __name__ == "__main__":
    unittest.main()
