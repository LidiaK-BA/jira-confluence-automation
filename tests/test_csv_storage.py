import csv
import tempfile
import unittest
from pathlib import Path

from tools.csv_storage import (
    DRAFT_FIELDS,
    REGISTRY_FIELDS,
    read_drafts,
    read_registry,
    write_drafts,
    write_registry,
)


class CsvStorageTests(unittest.TestCase):
    def setUp(self):
        self.record = {field: "" for field in REGISTRY_FIELDS}
        self.record.update(
            {
                "id": "CW-001",
                "title": 'Quote, "comma" and newline\n',
                "affected_systems": ["CargoWise", "TMS, Dispatch"],
                "document_links": ["https://example.test/doc?a=1&b=two"],
                "is_draft": False,
            }
        )

    def test_registry_round_trip_preserves_lists_and_special_characters(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "registry.csv"

            write_registry(path, [self.record])
            records = read_registry(path)

            self.assertEqual(records, [self.record])
            with path.open("r", encoding="utf-8", newline="") as csv_file:
                self.assertEqual(
                    next(csv.reader(csv_file)),
                    list(REGISTRY_FIELDS),
                )

    def test_drafts_round_trip_uses_stable_schema(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "drafts.csv"
            draft = {**self.record, "is_draft": True}

            write_drafts(path, [draft])

            self.assertEqual(read_drafts(path), [draft])
            with path.open("r", encoding="utf-8", newline="") as csv_file:
                self.assertEqual(next(csv.reader(csv_file)), list(DRAFT_FIELDS))

    def test_failed_write_leaves_existing_file_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "registry.csv"
            path.write_text("existing contents\n", encoding="utf-8")
            invalid_record = {**self.record, "is_draft": "sometimes"}

            with self.assertRaisesRegex(ValueError, "invalid is_draft"):
                write_registry(path, [invalid_record])

            self.assertEqual(path.read_text(encoding="utf-8"), "existing contents\n")

    def test_rejects_unexpected_headers(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "drafts.csv"
            path.write_text("id,title\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "expected columns"):
                read_drafts(path)


if __name__ == "__main__":
    unittest.main()
