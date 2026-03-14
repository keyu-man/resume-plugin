#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_TEMPLATE_PATH = REPO_ROOT / "template" / "data_template.json"


def clone_template(value):
  return copy.deepcopy(value)


def is_blank_scalar(value) -> bool:
  return value is None or (isinstance(value, str) and not value.strip())


def has_meaningful_content(value, *, ignore_index: bool = False) -> bool:
  if isinstance(value, dict):
    for key, item in value.items():
      if ignore_index and key == "index":
        continue
      if has_meaningful_content(item, ignore_index=ignore_index):
        return True
    return False

  if isinstance(value, list):
    return any(has_meaningful_content(item, ignore_index=ignore_index) for item in value)

  return not is_blank_scalar(value)


def normalize_value(candidate, template):
  if isinstance(template, dict):
    candidate_dict = candidate if isinstance(candidate, dict) else {}
    normalized = {}

    for key, template_value in template.items():
      normalized[key] = normalize_value(candidate_dict.get(key), template_value)

    return normalized

  if isinstance(template, list):
    item_template = template[0] if template else None
    candidate_list = candidate if isinstance(candidate, list) else []

    if item_template is None:
      return candidate_list

    normalized_items = [
      normalize_value(item, item_template)
      for item in candidate_list
      if has_meaningful_content(item)
    ]

    if isinstance(item_template, dict):
      normalized_items = [
        item
        for item in normalized_items
        if has_meaningful_content(item, ignore_index=True)
      ]

      if "index" in item_template:
        for index, item in enumerate(normalized_items, start=1):
          item["index"] = index

    return normalized_items

  if candidate is None:
    return clone_template(template)

  if isinstance(candidate, str):
    return candidate.strip()

  return candidate


def main() -> int:
  parser = argparse.ArgumentParser(
    description="Normalize a candidate resume JSON file against the repo template.",
  )
  parser.add_argument("input_json", help="Path to the candidate resume JSON file")
  parser.add_argument(
    "-o",
    "--output",
    help="Path to the normalized JSON file. Defaults to overwriting the input file.",
  )
  parser.add_argument(
    "-t",
    "--template",
    default=str(DEFAULT_TEMPLATE_PATH),
    help="Path to the JSON template file",
  )
  args = parser.parse_args()

  input_path = Path(args.input_json).expanduser().resolve()
  output_path = Path(args.output).expanduser().resolve() if args.output else input_path
  template_path = Path(args.template).expanduser().resolve()

  if not input_path.is_file():
    raise SystemExit(f"Input JSON not found: {input_path}")
  if not template_path.is_file():
    raise SystemExit(f"Template JSON not found: {template_path}")

  candidate = json.loads(input_path.read_text(encoding="utf-8"))
  template = json.loads(template_path.read_text(encoding="utf-8"))
  normalized = normalize_value(candidate, template)

  output_path.parent.mkdir(parents=True, exist_ok=True)
  output_path.write_text(
    json.dumps(normalized, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
  )
  print(output_path)
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
