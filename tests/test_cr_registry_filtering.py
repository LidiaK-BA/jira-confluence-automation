import contextlib
import csv
import io
import json
import tempfile
import unittest
from pathlib import Path

from cr_registry.cli import main
from cr_registry.filtering import filter_crs
from cr_registry.storage import REGISTRY_FIELDS


class FilterCRsTests(unittest.TestCase):
    def setUp(self):
        self.records = [
            {
                "id": "CW-001",
                "sub_project": "Alpha",
                "status": "Dev",
                "priority": "High",
                "owner": "Alex",
                "is_draft": False,
            },
            {
                "id": "CW-002",
                "sub_project": "Beta",
                "status": "Open",
                "priority": "High",
                "owner": "Alex",
                "is_draft": False,
            },
            {
                "id": "CW-003",
                "sub_project": "Alpha",
                "status": "Dev",
                "priority": "High",
                "owner": "Alex",
                "is_draft": True,
            },
            {
                "id": "CW-004",
                "sub_project": "Alpha",
                "status": "Dev",
                "priority": "Low",
                "owner": "Sam",
                "is_draft": False,
            },
        ]
        self.configured_sub_projects = ("Alpha", "Beta")

    def test_returns_records_in_input_order_and_excludes_drafts(self):
        result = filter_crs(
            self.records,
            configured_sub_projects=self.configured_sub_projects,
        )

        self.assertEqual([record["id"] for record in result], ["CW-001", "CW-002", "CW-004"])

    def test_applies_all_supplied_filters(self):
        result = filter_crs(
            self.records,
            configured_sub_projects=self.configured_sub_projects,
            sub_project="Alpha",
            status="Dev",
            priority="High",
            owner="Alex",
        )

        self.assertEqual([record["id"] for record in result], ["CW-001"])
        self.assertTrue(self.records[0]["is_draft"] is False)

    def test_rejects_unconfigured_sub_project(self):
        with self.assertRaisesRegex(ValueError, "unknown sub-project"):
            filter_crs(
                self.records,
                configured_sub_projects=self.configured_sub_projects,
                sub_project="Gamma",
            )

    def test_rejects_sub_project_when_none_are_configured(self):
        with self.assertRaisesRegex(ValueError, "no sub-projects are configured"):
            filter_crs(
                self.records,
                configured_sub_projects=(),
                sub_project="Alpha",
            )

    def test_rejects_unknown_status_and_priority(self):
        for filter_values, message in (
            ({"status": "Unknown"}, "unknown status"),
            ({"priority": "Urgent"}, "unknown priority"),
        ):
            with self.subTest(filter_values=filter_values):
                with self.assertRaisesRegex(ValueError, message):
                    filter_crs(
                        self.records,
                        configured_sub_projects=self.configured_sub_projects,
                        **filter_values,
                    )

    def test_cli_prints_matching_records_as_csv(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            config_path = root / "config.json"
            registry_path = root / "registry.csv"
            config_path.write_text(
                json.dumps({"sub_projects": ["Alpha", "Beta"]}), encoding="utf-8"
            )
            rows = [
                {
                    "id": "CW-001",
                    "title": "First",
                    "sub_project": "Alpha",
                    "owner": "Alex",
                    "priority": "High",
                    "status": "Dev",
                    "cost": "123.45",
                    "is_draft": "false",
                },
                {
                    "id": "CW-002",
                    "title": "Draft",
                    "sub_project": "Alpha",
                    "owner": "Alex",
                    "priority": "High",
                    "status": "Dev",
                    "is_draft": "true",
                },
                {
                    "id": "CW-003",
                    "title": "Second",
                    "sub_project": "Beta",
                    "owner": "Sam",
                    "priority": "Low",
                    "status": "Open",
                    "is_draft": "false",
                },
            ]
            with registry_path.open("w", encoding="utf-8", newline="") as registry_file:
                writer = csv.DictWriter(registry_file, fieldnames=REGISTRY_FIELDS)
                writer.writeheader()
                writer.writerows(rows)

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                exit_code = main(
                    [
                        "list",
                        "--config",
                        str(config_path),
                        "--registry",
                        str(registry_path),
                        "--sub-project",
                        "Alpha",
                        "--status",
                        "Dev",
                    ]
                )

        result_rows = list(csv.DictReader(io.StringIO(output.getvalue())))
        self.assertEqual(exit_code, 0)
        self.assertEqual([row["id"] for row in result_rows], ["CW-001"])
        self.assertNotIn("cost", result_rows[0])
        self.assertEqual(result_rows[0]["is_draft"], "false")


if __name__ == "__main__":
    unittest.main()
