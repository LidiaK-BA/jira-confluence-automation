import csv
import json
import os
import tempfile
from collections.abc import Mapping, Sequence
from pathlib import Path


REGISTRY_FIELDS = (
    "id",
    "title",
    "description",
    "sub_project",
    "requester",
    "owner",
    "priority",
    "status",
    "scope_impact",
    "effort_hours",
    "schedule_impact",
    "cost",
    "affected_systems",
    "jira_url",
    "document_links",
    "source_email_id",
    "created_date",
    "updated_date",
    "is_draft",
)
DRAFT_FIELDS = REGISTRY_FIELDS
LIST_FIELDS = ("affected_systems", "document_links")
Record = dict[str, object]


def _read_records(path: Path, fields: tuple[str, ...], label: str) -> list[Record]:
    with path.open("r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        if tuple(reader.fieldnames or ()) != fields:
            raise ValueError(f"{label} CSV must have the expected columns in order")

        records: list[Record] = []
        for line_number, row in enumerate(reader, start=2):
            if None in row:
                raise ValueError(f"{label} CSV row {line_number} has extra fields")
            if any(value is None for value in row.values()):
                raise ValueError(f"{label} CSV row {line_number} has missing fields")

            record: Record = dict(row)
            for field in LIST_FIELDS:
                raw_list = record[field]
                if raw_list == "":
                    record[field] = []
                    continue
                try:
                    values = json.loads(raw_list)
                except json.JSONDecodeError as error:
                    raise ValueError(
                        f"{label} CSV row {line_number} has invalid {field} JSON"
                    ) from error
                if not isinstance(values, list) or any(
                    not isinstance(value, str) for value in values
                ):
                    raise ValueError(
                        f"{label} CSV row {line_number} has invalid {field} value"
                    )
                record[field] = values

            raw_draft = record["is_draft"]
            if raw_draft.strip().lower() not in ("true", "false"):
                raise ValueError(
                    f"{label} CSV row {line_number} has invalid is_draft value"
                )
            record["is_draft"] = raw_draft.strip().lower() == "true"
            records.append(record)
    return records


def _write_records(
    path: Path,
    records: Sequence[Mapping[str, object]],
    fields: tuple[str, ...],
    label: str,
) -> None:
    serialized_records: list[dict[str, str]] = []
    allowed_fields = set(fields)
    for row_number, record in enumerate(records, start=1):
        unknown_fields = set(record) - allowed_fields
        if unknown_fields:
            names = ", ".join(sorted(unknown_fields))
            raise ValueError(f"{label} record {row_number} has unknown fields: {names}")
        if "is_draft" not in record:
            raise ValueError(f"{label} record {row_number} is missing is_draft")

        serialized: dict[str, str] = {}
        for field in fields:
            value = record.get(field, "")
            if field in LIST_FIELDS:
                if value == "":
                    serialized[field] = ""
                elif isinstance(value, (list, tuple)) and all(
                    isinstance(item, str) for item in value
                ):
                    serialized[field] = json.dumps(
                        list(value), ensure_ascii=False, separators=(",", ":")
                    )
                else:
                    raise ValueError(
                        f"{label} record {row_number} field {field} must be a list "
                        "of strings"
                    )
            elif field == "is_draft":
                if isinstance(value, bool):
                    serialized[field] = str(value).lower()
                elif isinstance(value, str) and value.strip().lower() in (
                    "true",
                    "false",
                ):
                    serialized[field] = value.strip().lower()
                else:
                    raise ValueError(
                        f"{label} record {row_number} has invalid is_draft value"
                    )
            elif value is None:
                serialized[field] = ""
            else:
                serialized[field] = str(value)
        serialized_records.append(serialized)

    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            writer = csv.DictWriter(
                temporary_file, fieldnames=fields, lineterminator="\n"
            )
            writer.writeheader()
            writer.writerows(serialized_records)
            temporary_file.flush()
            os.fsync(temporary_file.fileno())
        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def read_registry(path: Path) -> list[Record]:
    return _read_records(path, REGISTRY_FIELDS, "registry")


def write_registry(path: Path, records: Sequence[Mapping[str, object]]) -> None:
    _write_records(path, records, REGISTRY_FIELDS, "registry")


def read_drafts(path: Path) -> list[Record]:
    return _read_records(path, DRAFT_FIELDS, "drafts")


def write_drafts(path: Path, records: Sequence[Mapping[str, object]]) -> None:
    _write_records(path, records, DRAFT_FIELDS, "drafts")


def serialize_csv_value(value: object) -> str:
    if isinstance(value, (list, tuple)) and all(
        isinstance(item, str) for item in value
    ):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    if isinstance(value, bool):
        return str(value).lower()
    return "" if value is None else str(value)
