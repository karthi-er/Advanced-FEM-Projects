"""Command-line entry point for control-log analysis."""

import argparse
import sys

from .analysis import analyze_csv


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize a recorded control log.")
    parser.add_argument("csv_file", help="CSV file with time,setpoint,output columns")
    args = parser.parse_args()
    try:
        metrics = analyze_csv(args.csv_file)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(f"samples: {metrics.sample_count}")
    print(f"tracking RMSE: {metrics.rmse:.6g}")
    print(f"maximum absolute error: {metrics.max_abs_error:.6g}")
    print(f"final error: {metrics.final_error:.6g}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
