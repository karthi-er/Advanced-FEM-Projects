"""Run the built-in two-element axial-bar example."""

from .solver import Element, solve


def main() -> None:
    result = solve(
        node_positions=[0.0, 1.0, 2.0],
        elements=[
            Element(0, 1, youngs_modulus=200e9, area=1e-4),
            Element(1, 2, youngs_modulus=200e9, area=1e-4),
        ],
        loads={2: 1000.0},
        prescribed_displacements={0: 0.0},
    )
    print("Illustrative 1D axial-bar FEM run (consistent SI units)")
    print("nodal displacements [m]:", ", ".join(f"{value:.6g}" for value in result.displacements))
    print("element axial forces [N]:", ", ".join(f"{value:.6g}" for value in result.axial_forces))


if __name__ == "__main__":
    main()
