"""Read CFD comparison records while retaining invalid and duplicate entries."""

import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence


REQUIRED_COLUMNS = ("material", "velocity", "quantity", "value", "provenance")


@dataclass(frozen=True)
class CFDReport:
    record_count: int
    valid_record_count: int
    invalid_rows: tuple[dict, ...]
    duplicate_keys: tuple[str, ...]
    missing_combinations: tuple[str, ...]
    unexpected_combinations: tuple[str, ...]
    comparison_complete: bool | None
    provenance_values: tuple[str, ...]

    def to_dict(self) -> dict:
        return {
            "record_count": self.record_count,
            "valid_record_count": self.valid_record_count,
            "invalid_rows": list(self.invalid_rows),
            "duplicate_keys": list(self.duplicate_keys),
            "missing_combinations": list(self.missing_combinations),
            "unexpected_combinations": list(self.unexpected_combinations),
            "comparison_complete": self.comparison_complete,
            "provenance_values": list(self.provenance_values),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


def _expected_values(values: Sequence[str] | None, label: str) -> list[str] | None:
    if values is None:
        return None
    cleaned = [item.strip() for item in values]
    if not cleaned or any(not item for item in cleaned):
        raise ValueError(f"expected {label} must contain non-empty values")
    if len(set(cleaned)) != len(cleaned):
        raise ValueError(f"expected {label} must not contain duplicates")
    return cleaned


def analyze_records(
    rows: Iterable[Mapping[str, object]],
    expected_materials: Sequence[str] | None = None,
    expected_velocities: Sequence[str] | None = None,
    expected_quantities: Sequence[str] | None = None,
) -> CFDReport:
    """Report malformed records, duplicate keys, and missing expected cells."""
    materials = _expected_values(expected_materials, "materials")
    velocities = _expected_values(expected_velocities, "velocities")
    quantities = _expected_values(expected_quantities, "quantities")
    dimensions_declared = all(value is not None for value in (materials, velocities, quantities))

    invalid_rows = []
    duplicate_keys = set()
    seen = set()
    valid_keys = set()
    provenance_values = set()
    unexpected_keys = set()
    total = 0
    valid_count = 0

    for row_number, row in enumerate(rows, start=2):
        total += 1
        if None in row:
            invalid_rows.append({
                "row": row_number,
                "reason": "row contains more fields than the CSV header",
                "data": dict(row),
            })
            continue
        missing_columns = [column for column in REQUIRED_COLUMNS if column not in row]
        if missing_columns:
            invalid_rows.append({
                "row": row_number,
                "reason": f"missing column(s): {', '.join(missing_columns)}",
                "data": dict(row),
            })
            continue
        material = str(row["material"]).strip()
        velocity = str(row["velocity"]).strip()
        quantity = str(row["quantity"]).strip()
        provenance = str(row["provenance"]).strip()
        value_text = str(row["value"]).strip()
        try:
            value = float(value_text)
        except ValueError:
            value = math.nan
        if not material or not velocity or not quantity or not provenance:
            reason = "material, velocity, quantity, and provenance must not be blank"
        elif not math.isfinite(value):
            reason = "value must be a finite number"
        else:
            reason = ""
        key = (material, velocity, quantity)
        if dimensions_declared and (
            material not in materials or velocity not in velocities or quantity not in quantities
        ):
            unexpected_keys.add(" / ".join(key))
        if key in seen:
            duplicate_keys.add(" / ".join(key))
        seen.add(key)
        provenance_values.add(provenance)
        if reason:
            invalid_rows.append({"row": row_number, "reason": reason, "data": dict(row)})
            continue
        valid_count += 1
        valid_keys.add(key)

    missing_combinations = []
    if dimensions_declared:
        for material in materials:
            for velocity in velocities:
                for quantity in quantities:
                    key = (material, velocity, quantity)
                    if key not in valid_keys:
                        missing_combinations.append(" / ".join(key))
        complete = (
            not invalid_rows
            and not duplicate_keys
            and not missing_combinations
            and not unexpected_keys
        )
    else:
        complete = None

    return CFDReport(
        record_count=total,
        valid_record_count=valid_count,
        invalid_rows=tuple(invalid_rows),
        duplicate_keys=tuple(sorted(duplicate_keys)),
        missing_combinations=tuple(missing_combinations),
        unexpected_combinations=tuple(sorted(unexpected_keys)),
        comparison_complete=complete,
        provenance_values=tuple(sorted(provenance_values)),
    )


def read_csv_report(
    path: str | Path,
    expected_materials: Sequence[str] | None = None,
    expected_velocities: Sequence[str] | None = None,
    expected_quantities: Sequence[str] | None = None,
) -> CFDReport:
    source = Path(path)
    try:
        with source.open("r", newline="", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            if reader.fieldnames is None:
                raise ValueError("CSV is missing a header row")
            missing = [column for column in REQUIRED_COLUMNS if column not in reader.fieldnames]
            if missing:
                raise ValueError(f"CSV is missing required column(s): {', '.join(missing)}")
            return analyze_records(
                reader, expected_materials, expected_velocities, expected_quantities
            )
    except (OSError, UnicodeError) as exc:
        raise ValueError(f"cannot read input file '{source}': {exc}") from exc
