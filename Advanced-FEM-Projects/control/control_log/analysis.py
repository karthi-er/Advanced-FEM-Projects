"""Input validation and descriptive metrics for recorded setpoint/output logs."""

import csv
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping


@dataclass(frozen=True)
class LogMetrics:
    sample_count: int
    rmse: float
    max_abs_error: float
    final_error: float


def _finite_number(value: object, field: str, row_number: int) -> float:
    try:
        number = float(value)
    except (OverflowError, TypeError, ValueError) as exc:
        raise ValueError(f"row {row_number}: {field} must be a number") from exc
    if not math.isfinite(number):
        raise ValueError(f"row {row_number}: {field} must be finite")
    return number


def analyze_samples(rows: Iterable[Mapping[str, object]]) -> LogMetrics:
    """Compute tracking-error metrics from time-ordered input rows."""
    count = 0
    previous_time = -math.inf
    squared_error_sum = 0.0
    max_abs_error = 0.0
    final_error = 0.0

    for row_number, row in enumerate(rows, start=2):
        missing = [field for field in ("time", "setpoint", "output") if field not in row]
        if missing:
            raise ValueError(f"row {row_number}: missing column(s): {', '.join(missing)}")
        time = _finite_number(row["time"], "time", row_number)
        setpoint = _finite_number(row["setpoint"], "setpoint", row_number)
        output = _finite_number(row["output"], "output", row_number)
        if time <= previous_time:
            raise ValueError(f"row {row_number}: time must be strictly increasing")

        error = setpoint - output
        if not math.isfinite(error):
            raise ValueError(f"row {row_number}: tracking error is outside the finite numeric range")
        squared_error = error * error
        if not math.isfinite(squared_error) or not math.isfinite(squared_error_sum + squared_error):
            raise ValueError(f"row {row_number}: tracking error is too large to calculate RMSE")
        squared_error_sum += squared_error
        max_abs_error = max(max_abs_error, abs(error))
        final_error = error
        previous_time = time
        count += 1

    if count == 0:
        raise ValueError("input must contain at least one data row")
    return LogMetrics(
        sample_count=count,
        rmse=math.sqrt(squared_error_sum / count),
        max_abs_error=max_abs_error,
        final_error=final_error,
    )


def analyze_csv(path: str | Path) -> LogMetrics:
    """Read and analyze a CSV with time, setpoint, and output columns."""
    source = Path(path)
    try:
        with source.open("r", newline="", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            if reader.fieldnames is None:
                raise ValueError("CSV is missing a header row")
            missing = [field for field in ("time", "setpoint", "output") if field not in reader.fieldnames]
            if missing:
                raise ValueError(f"CSV is missing required column(s): {', '.join(missing)}")
            return analyze_samples(reader)
    except (OSError, UnicodeError) as exc:
        raise ValueError(f"cannot read input file '{source}': {exc}") from exc
