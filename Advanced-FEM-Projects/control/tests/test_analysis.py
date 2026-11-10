import math
import tempfile
import unittest
from pathlib import Path

from control_log import analyze_csv, analyze_samples


class AnalysisTests(unittest.TestCase):
    def test_metrics_for_valid_samples(self):
        result = analyze_samples([
            {"time": 0, "setpoint": 1, "output": 0},
            {"time": 1, "setpoint": 1, "output": 0.5},
        ])
        self.assertEqual(result.sample_count, 2)
        self.assertAlmostEqual(result.rmse, math.sqrt(0.625))
        self.assertEqual(result.max_abs_error, 1)
        self.assertEqual(result.final_error, 0.5)

    def test_rejects_non_finite_and_non_increasing_time(self):
        for rows in (
            [{"time": 0, "setpoint": float("nan"), "output": 0}],
            [{"time": 0, "setpoint": 1, "output": 0},
             {"time": 0, "setpoint": 1, "output": 0}],
        ):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                analyze_samples(rows)

    def test_rejects_metric_overflow_from_finite_inputs(self):
        with self.assertRaisesRegex(ValueError, "too large"):
            analyze_samples([{"time": 0, "setpoint": 1e200, "output": 0}])

    def test_csv_reports_missing_columns(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.csv"
            path.write_text("time,setpoint\n0,1\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "output"):
                analyze_csv(path)


if __name__ == "__main__":
    unittest.main()
