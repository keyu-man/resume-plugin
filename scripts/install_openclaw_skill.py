#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path


def main() -> int:
  parser = argparse.ArgumentParser(
    description="Copy a local skill into OpenClaw's managed skills directory.",
  )
  parser.add_argument(
    "--openclaw",
    default="openclaw",
    help="OpenClaw CLI binary to use",
  )
  parser.add_argument(
    "--skill-name",
    required=True,
    help="Installed skill name under the managed skills directory",
  )
  parser.add_argument(
    "--source",
    required=True,
    help="Path to the source skill directory",
  )
  args = parser.parse_args()

  source = Path(args.source).expanduser().resolve()
  if not source.is_dir():
    raise SystemExit(f"Skill source not found: {source}")

  payload = subprocess.check_output(
    [args.openclaw, "skills", "list", "--json"],
    text=True,
  )
  managed_dir = Path(json.loads(payload)["managedSkillsDir"]).expanduser()
  managed_dir.mkdir(parents=True, exist_ok=True)

  destination = managed_dir / args.skill_name
  if destination.is_symlink() or destination.is_file():
    destination.unlink()
  elif destination.exists():
    shutil.rmtree(destination)

  shutil.copytree(
    source,
    destination,
    ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"),
  )
  print(destination)
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
