import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Sequence

from .filtering import filter_crs
from .storage import REGISTRY_FIELDS, read_registry, serialize_csv_value


DEFAULT_CONFIG = Path("cr-registry") / "config.json"
DEFAULT_REGISTRY = Path("cr-registry") / "registry.csv"


def _load_config(path: Path) -> tuple[str, ...]:
    with path.open("r", encoding="utf-8") as config_file:
        config = json.load(config_file)
    if not isinstance(config, dict):
        raise ValueError("config must be a JSON object")
    sub_projects = config.get("sub_projects")
    if not isinstance(sub_projects, list) or any(
        not isinstance(item, str) or not item.strip() for item in sub_projects
    ):
        raise ValueError("config must define sub_projects as a list of non-empty names")
    if len(set(sub_projects)) != len(sub_projects):
        raise ValueError("config sub_projects must not contain duplicates")
    return tuple(sub_projects)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cr-registry")
    commands = parser.add_subparsers(dest="command", required=True)
    list_command = commands.add_parser("list", help="list confirmed change requests")
    list_command.add_argument("--sub-project")
    list_command.add_argument("--status")
    list_command.add_argument("--priority")
    list_command.add_argument("--owner")
    list_command.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    list_command.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)

    try:
        configured_sub_projects = _load_config(args.config)
        records = read_registry(args.registry)
        matching_records = filter_crs(
            records,
            configured_sub_projects=configured_sub_projects,
            sub_project=args.sub_project,
            status=args.status,
            priority=args.priority,
            owner=args.owner,
        )
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    writer = csv.DictWriter(
        sys.stdout,
        fieldnames=tuple(field for field in REGISTRY_FIELDS if field != "cost"),
        extrasaction="ignore",
        lineterminator="\n",
    )
    writer.writeheader()
    for record in matching_records:
        output_record = dict(record)
        output_record["is_draft"] = "true" if record["is_draft"] else "false"
        writer.writerow(
            {key: serialize_csv_value(value) for key, value in output_record.items()}
        )
    return 0
