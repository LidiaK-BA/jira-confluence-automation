---
description: "Use when reading or writing registry and draft CSV files with tools/csv_storage.py."
---

- Use `tools.csv_storage` for CSV persistence of change-request registry and draft records.
- Call `read_registry(path)` / `write_registry(path, records)` for `registry.csv`; call `read_drafts(path)` / `write_drafts(path, records)` for `drafts.csv`. Pass `path` as a `Path`.
- Use records with the established `REGISTRY_FIELDS` / `DRAFT_FIELDS` schema. Include `is_draft` when writing; reject unknown fields rather than silently dropping them.
- Represent `affected_systems` and `document_links` as lists or tuples of strings when writing. Reads return these fields as lists and `is_draft` as a boolean; other values remain strings.
- Preserve the stable field order and let the module serialize list fields as JSON and replace files atomically. Ensure the destination directory exists before writing.
- Use `serialize_csv_value(value)` when rendering a value with `csv.DictWriter`; it serializes lists and booleans consistently with the storage format.
- Surface `OSError` and `ValueError` from storage operations to the caller; do not silently ignore malformed headers, rows, or values.
