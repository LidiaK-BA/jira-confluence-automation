import csv
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


def read_registry(path: Path) -> list[dict[str, object]]:
    with path.open("r", encoding="utf-8", newline="") as registry_file:
        reader = csv.DictReader(registry_file)
        if reader.fieldnames is None or "is_draft" not in reader.fieldnames:
            raise ValueError("registry CSV must have an is_draft column")

        records: list[dict[str, object]] = []
        for line_number, row in enumerate(reader, start=2):
            if None in row:
                raise ValueError(f"registry CSV row {line_number} has extra fields")
            record: dict[str, object] = dict(row)
            raw_draft = row.get("is_draft")
            if raw_draft is None or raw_draft.strip().lower() not in ("true", "false"):
                raise ValueError(
                    f"registry CSV row {line_number} has invalid is_draft value"
                )
            record["is_draft"] = raw_draft.strip().lower() == "true"
            records.append(record)
    return records
