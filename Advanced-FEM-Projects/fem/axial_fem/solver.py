"""Linear 1D axial-bar finite elements with prescribed displacements."""

import math
from dataclasses import dataclass
from typing import Mapping, Sequence


@dataclass(frozen=True)
class Element:
    start: int
    end: int
    youngs_modulus: float
    area: float


@dataclass(frozen=True)
class FEMResult:
    displacements: tuple[float, ...]
    axial_forces: tuple[float, ...]


def _number(value: object, label: str) -> float:
    try:
        result = float(value)
    except (OverflowError, TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be a number") from exc
    if not math.isfinite(result):
        raise ValueError(f"{label} must be finite")
    return result


def _solve_dense(matrix: list[list[float]], vector: list[float]) -> list[float]:
    size = len(vector)
    augmented = [row[:] + [value] for row, value in zip(matrix, vector)]
    for column in range(size):
        pivot = max(range(column, size), key=lambda row: abs(augmented[row][column]))
        if abs(augmented[pivot][column]) < 1e-14:
            raise ValueError("system is singular; check supports and element connectivity")
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        scale = augmented[column][column]
        for j in range(column, size + 1):
            augmented[column][j] /= scale
        for row in range(size):
            if row == column:
                continue
            factor = augmented[row][column]
            for j in range(column, size + 1):
                augmented[row][j] -= factor * augmented[column][j]
    result = [augmented[row][size] for row in range(size)]
    if not all(math.isfinite(value) for value in result):
        raise ValueError("solution is outside the finite numeric range")
    return result


def solve(
    node_positions: Sequence[float],
    elements: Sequence[Element],
    loads: Mapping[int, float],
    prescribed_displacements: Mapping[int, float],
) -> FEMResult:
    """Assemble and solve a linear axial-bar model in consistent units."""
    positions = [_number(value, f"node {index} position") for index, value in enumerate(node_positions)]
    count = len(positions)
    if count < 2:
        raise ValueError("model must contain at least two nodes")
    if not elements:
        raise ValueError("model must contain at least one element")
    if not prescribed_displacements:
        raise ValueError("at least one prescribed displacement is required")

    stiffness = [[0.0] * count for _ in range(count)]
    force = [0.0] * count
    for node, value in loads.items():
        if not isinstance(node, int) or not 0 <= node < count:
            raise ValueError(f"load references invalid node {node!r}")
        force[node] += _number(value, f"load at node {node}")
        if not math.isfinite(force[node]):
            raise ValueError(f"combined load at node {node} is outside the finite numeric range")

    for index, element in enumerate(elements):
        if not (isinstance(element.start, int) and isinstance(element.end, int)
                and 0 <= element.start < count and 0 <= element.end < count):
            raise ValueError(f"element {index} references an invalid node")
        if element.start == element.end:
            raise ValueError(f"element {index} must connect two different nodes")
        length = abs(positions[element.end] - positions[element.start])
        if not math.isfinite(length):
            raise ValueError(f"element {index} length is outside the finite numeric range")
        modulus = _number(element.youngs_modulus, f"element {index} Young's modulus")
        area = _number(element.area, f"element {index} area")
        if length == 0:
            raise ValueError(f"element {index} has zero length")
        if modulus <= 0 or area <= 0:
            raise ValueError(f"element {index} modulus and area must be positive")
        coefficient = modulus * area / length
        if not math.isfinite(coefficient):
            raise ValueError(f"element {index} stiffness is outside the finite numeric range")
        i, j = element.start, element.end
        stiffness[i][i] += coefficient
        stiffness[i][j] -= coefficient
        stiffness[j][i] -= coefficient
        stiffness[j][j] += coefficient
        if not all(math.isfinite(value) for value in (
            stiffness[i][i], stiffness[i][j], stiffness[j][i], stiffness[j][j]
        )):
            raise ValueError("assembled stiffness is outside the finite numeric range")

    fixed = {}
    for node, value in prescribed_displacements.items():
        if not isinstance(node, int) or not 0 <= node < count:
            raise ValueError(f"prescribed displacement references invalid node {node!r}")
        fixed[node] = _number(value, f"prescribed displacement at node {node}")
    free = [node for node in range(count) if node not in fixed]
    displacement = [0.0] * count
    for node, value in fixed.items():
        displacement[node] = value
    if free:
        reduced_matrix = [[stiffness[i][j] for j in free] for i in free]
        reduced_force = [
            force[i] - sum(stiffness[i][j] * displacement[j] for j in fixed)
            for i in free
        ]
        if not all(math.isfinite(value) for value in reduced_force):
            raise ValueError("reduced force vector is outside the finite numeric range")
        solved = _solve_dense(reduced_matrix, reduced_force)
        for node, value in zip(free, solved):
            displacement[node] = value

    axial_forces = []
    for element in elements:
        length = abs(positions[element.end] - positions[element.start])
        strain = (displacement[element.end] - displacement[element.start]) / length
        axial_force = (
            _number(element.youngs_modulus, "Young's modulus")
            * _number(element.area, "area")
            * strain
        )
        if not math.isfinite(axial_force):
            raise ValueError("element axial force is outside the finite numeric range")
        axial_forces.append(axial_force)
    return FEMResult(tuple(displacement), tuple(axial_forces))
