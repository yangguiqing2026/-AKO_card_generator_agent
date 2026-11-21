# ============================================
# Author: AKO_studio
# Agent: AKO_card_generator
# Form <-> config conversion helpers (no tkinter dependency)
# ============================================

import json

try:
    import yaml
except ImportError as exc:  # pragma: no cover - depends on runtime environment
    yaml = None
    _YAML_IMPORT_ERROR = exc
else:
    _YAML_IMPORT_ERROR = None

from .card_generator import (
    DEFAULT_OUTPUT,
    DICT_FIELDS,
    LIST_FIELDS,
    REQUIRED_STRING_FIELDS,
)

# Order used when rendering the form and when flattening a config back to it.
FORM_STRING_FIELDS = REQUIRED_STRING_FIELDS
FORM_LIST_FIELDS = LIST_FIELDS
FORM_DICT_FIELDS = DICT_FIELDS
FORM_OPTIONAL_FIELDS = ("log_level",)

ALL_AGENT_FIELDS = (
    FORM_STRING_FIELDS
    + FORM_LIST_FIELDS
    + FORM_DICT_FIELDS
    + FORM_OPTIONAL_FIELDS
)

OUTPUT_PATH_KEY = "output_path"


def _require_yaml():
    if yaml is None:
        raise RuntimeError(
            "PyYAML 未安装，请先执行: python -m pip install -r requirements.txt"
        ) from _YAML_IMPORT_ERROR


def parse_list(text):
    """Parse a text area into a list of trimmed non-empty lines.

    Optional leading ``- `` bullets are stripped so pasted YAML lists work.
    """
    if not text:
        return []
    items = []
    for raw_line in str(text).splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("- "):
            line = line[2:].strip()
        elif line == "-":
            continue
        if line:
            items.append(line)
    return items


def parse_mapping(text):
    """Parse ``key=value`` lines into a mapping.

    Values are parsed with ``yaml.safe_load`` so booleans, numbers and quoted
    strings keep their types. Lines without ``=`` (or blank/comment lines) are
    reported back so the GUI can warn the user without losing valid rows.

    Returns (mapping, bad_lines).
    """
    _require_yaml()
    mapping = {}
    bad_lines = []
    if not text:
        return mapping, bad_lines

    for raw_line in str(text).splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            bad_lines.append(raw_line)
            continue
        key, raw_value = line.split("=", 1)
        key = key.strip()
        if not key:
            bad_lines.append(raw_line)
            continue
        value_text = raw_value.strip()
        if value_text == "":
            value = ""
        else:
            try:
                value = yaml.safe_load(value_text)
            except yaml.YAMLError:
                # Fall back to a literal string for anything YAML cannot parse.
                value = value_text
        mapping[key] = value
    return mapping, bad_lines


def _format_scalar(value):
    """Render a scalar as a single-line string that round-trips through YAML."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    return json.dumps(str(value), ensure_ascii=False)


def format_list(items):
    """Render a list as one item per line for a text area."""
    if not items:
        return ""
    return "\n".join(str(item) for item in items)


def format_mapping(mapping):
    """Render a mapping as ``key=value`` lines for a text area."""
    if not mapping:
        return ""
    return "\n".join(
        "{}={}".format(key, _format_scalar(value)) for key, value in mapping.items()
    )


def form_to_config(values, output_path=None):
    """Build a config mapping from GUI field values.

    ``values`` is a mapping keyed by agent field names; list/dict fields hold
    text-area strings. Returns a config dict ready for validate/build/write.
    """
    agent = {}
    for field in FORM_STRING_FIELDS:
        agent[field] = str(values.get(field, "") or "").strip()

    for field in FORM_LIST_FIELDS:
        agent[field] = parse_list(values.get(field, ""))

    for field in FORM_DICT_FIELDS:
        mapping, _bad = parse_mapping(values.get(field, ""))
        agent[field] = mapping

    log_level = str(values.get("log_level", "") or "").strip()
    if log_level:
        agent["log_level"] = log_level

    path = (output_path or values.get(OUTPUT_PATH_KEY) or "").strip() or DEFAULT_OUTPUT
    return {"agent": agent, "output": {"path": path}}


def config_to_form(config):
    """Flatten a config mapping into GUI field values (inverse of form_to_config)."""
    agent = (config or {}).get("agent") or {}
    values = {}
    for field in FORM_STRING_FIELDS:
        values[field] = str(agent.get(field, "") or "")
    for field in FORM_LIST_FIELDS:
        values[field] = format_list(agent.get(field) or [])
    for field in FORM_DICT_FIELDS:
        values[field] = format_mapping(agent.get(field) or {})
    for field in FORM_OPTIONAL_FIELDS:
        values[field] = str(agent.get(field, "") or "")
    output = (config or {}).get("output") or {}
    values[OUTPUT_PATH_KEY] = str(output.get("path") or DEFAULT_OUTPUT)
    return values
