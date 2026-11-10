import tempfile
import unittest
from pathlib import Path

from cfd_analysis import analyze_records, read_csv_report


class ReportTests(unittest.TestCase):
    def test_incomplete_and_duplicate_records_remain_visible(self):
        rows = [
            {"material": "Al", "velocity": "low", "quantity": "drag", "value": "1", "provenance": "synthetic"},
            {"material": "Al", "velocity": "low", "quantity": "drag", "value": "1.1", "provenance": "synthetic"},
            {"material": "Steel", "velocity": "high", "quantity": "drag", "value": "", "provenance": "fluent"},
        ]
        report = analyze_records(rows, ["Al", "Steel"], ["low", "high"], ["drag"])
        self.assertEqual(report.record_count, 3)
        self.assertEqual(report.valid_record_count, 2)
        self.assertEqual(len(report.invalid_rows), 1)
        self.assertIn("Al / low / drag", report.duplicate_keys)
        self.assertIn("Steel / low / drag", report.missing_combinations)
        self.assertFalse(report.comparison_complete)
        self.assertIn("fluent", report.provenance_values)

    def test_without_declared_grid_completeness_is_unassessed(self):
        report = analyze_records([])
        self.assertIsNone(report.comparison_complete)

    def test_csv_requires_schema(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing.csv"
            path.write_text("material,value\nAl,1\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "velocity"):
                read_csv_report(path)

    def test_expected_dimensions_reject_duplicates(self):
        with self.assertRaisesRegex(ValueError, "duplicates"):
            analyze_records([], ["Al", "Al"], ["low"], ["drag"])

    def test_unexpected_combinations_prevent_complete_status(self):
        report = analyze_records(
            [{"material": "Copper", "velocity": "low", "quantity": "drag",
              "value": "1", "provenance": "fluent"}],
            ["Al"], ["low"], ["drag"],
        )
        self.assertFalse(report.comparison_complete)
        self.assertEqual(report.unexpected_combinations, ("Copper / low / drag",))


if __name__ == "__main__":
    unittest.main()
