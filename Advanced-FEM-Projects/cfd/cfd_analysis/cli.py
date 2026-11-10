"""Command-line entry point for CFD CSV validation."""

import argparse
import sys

from .report import read_csv_report


def _csv_list(value: str | None) -> list[str] | None:
    return value.split(",") if value is not None else None


def main() -> int:
    parser = argparse.ArgumentParser(description="Check CFD export records and comparison completeness.")
    parser.add_argument("csv_file", help="CSV with material,velocity,quantity,value,provenance columns")
    parser.add_argument("--materials", help="Expected material names, comma-separated")
    parser.add_argument("--velocities", help="Expected velocity names/values, comma-separated")
    parser.add_argument("--quantities", help="Expected exported quantities, comma-separated")
    args = parser.parse_args()
    dimensions = (args.materials, args.velocities, args.quantities)
    if any(dimensions) and not all(dimensions):
        parser.error("--materials, --velocities, and --quantities must be supplied together")
    try:
        report = read_csv_report(
            args.csv_file,
            _csv_list(args.materials),
            _csv_list(args.velocities),
            _csv_list(args.quantities),
        )
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(report.to_json())
    if report.comparison_complete is None:
        print("Comparison completeness: NOT ASSESSED (declare the expected grid).")
    elif report.comparison_complete:
        print("Comparison completeness: complete for the declared grid.")
    else:
        print("Comparison completeness: INCOMPLETE; inspect invalid, duplicate, and missing entries.")
    if any(value.lower() == "synthetic" for value in report.provenance_values):
        print("DATA STATUS: SYNTHETIC EXAMPLE ONLY - not Fluent simulation findings.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
