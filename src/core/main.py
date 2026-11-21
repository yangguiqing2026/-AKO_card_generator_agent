# ============================================
# Author: AKO_studio
# Agent: AKO_card_generator
# Generated: 2026-07-30
# ============================================

import argparse
import logging
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.card_generator import (  # noqa: E402
    generate_card,
    load_config,
    validate_card_config,
)


def setup_logging(level="INFO"):
    """Configure console + file logging; safe to call more than once."""
    numeric_level = getattr(logging, str(level).upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError("无效日志级别: {}".format(level))

    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    root_logger = logging.getLogger()
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)
        handler.close()

    root_logger.setLevel(numeric_level)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    root_logger.addHandler(stream_handler)

    file_handler = logging.FileHandler(
        log_dir / "AKO_card_generator.log", encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Ako Card Generator")
    parser.add_argument(
        "--config",
        default="config/AKO_card_generator_config.yaml",
        help="Configuration file path",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output card path (overrides output.path in config)",
    )
    parser.add_argument(
        "--log-level",
        default=None,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Log level (overrides agent.log_level in config)",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    setup_logging(args.log_level or "INFO")
    logger = logging.getLogger("AKO_card_generator")

    try:
        config = load_config(args.config)
        agent = validate_card_config(config)

        effective_level = args.log_level or agent.get("log_level") or "INFO"
        if effective_level.upper() != (args.log_level or "INFO").upper():
            setup_logging(effective_level)
            logger = logging.getLogger("AKO_card_generator")

        logger.info("Ako Card Generator starting...")
        logger.info("Config: %s", args.config)
        logger.info("Log level: %s", effective_level.upper())

        output_path, card = generate_card(args.config, args.output)
        logger.info("Agent card generated: %s", output_path)
        logger.info("Agent id: %s", card["agent_id"])
    except (FileNotFoundError, ValueError, RuntimeError, OSError) as exc:
        logger.error("Failed to generate agent card: %s", exc)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
