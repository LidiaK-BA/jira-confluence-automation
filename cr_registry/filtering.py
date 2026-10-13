from collections.abc import Iterable, Mapping


STATUSES = (
    "Open",
    "Requirements and Discovery",
    "Ready for Dev",
    "Dev",
    "Ready for Testing",
    "In Testing",
    "On Hold",
    "Closed",
    "Rejected",
)
PRIORITIES = ("High", "Med", "Low")


def filter_crs(
    records: Iterable[Mapping[str, object]],
    *,
    configured_sub_projects: Iterable[str],
    sub_project: str | None = None,
    status: str | None = None,
    priority: str | None = None,
    owner: str | None = None,
) -> list[Mapping[str, object]]:
    """Return confirmed records matching every supplied filter, in input order."""
    valid_sub_projects = tuple(configured_sub_projects)

    if sub_project is not None and sub_project not in valid_sub_projects:
        if valid_sub_projects:
            allowed = ", ".join(valid_sub_projects)
            raise ValueError(
                f"unknown sub-project {sub_project!r}; configured values: {allowed}"
            )
        raise ValueError("no sub-projects are configured")
    if status is not None and status not in STATUSES:
        raise ValueError(
            f"unknown status {status!r}; expected one of: {', '.join(STATUSES)}"
        )
    if priority is not None and priority not in PRIORITIES:
        raise ValueError(
            f"unknown priority {priority!r}; expected one of: {', '.join(PRIORITIES)}"
        )

    matches: list[Mapping[str, object]] = []
    for record in records:
        if _is_draft(record.get("is_draft")):
            continue
        if sub_project is not None and record.get("sub_project") != sub_project:
            continue
        if status is not None and record.get("status") != status:
            continue
        if priority is not None and record.get("priority") != priority:
            continue
        if owner is not None and record.get("owner") != owner:
            continue
        matches.append(record)
    return matches


def _is_draft(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized == "true":
            return True
        if normalized == "false":
            return False
    raise ValueError(f"invalid is_draft value: {value!r}")
