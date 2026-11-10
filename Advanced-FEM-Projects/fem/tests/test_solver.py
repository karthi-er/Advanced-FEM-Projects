import unittest

from axial_fem import Element, solve


class SolverTests(unittest.TestCase):
    def test_two_element_bar_load(self):
        result = solve(
            [0, 1, 2],
            [Element(0, 1, 200, 2), Element(1, 2, 200, 2)],
            {2: 10},
            {0: 0},
        )
        self.assertAlmostEqual(result.displacements[1], 0.025)
        self.assertAlmostEqual(result.displacements[2], 0.05)
        self.assertEqual(result.axial_forces, (10, 10))

    def test_rejects_non_finite_material_and_unconstrained_model(self):
        with self.assertRaisesRegex(ValueError, "finite"):
            solve([0, 1], [Element(0, 1, float("inf"), 1)], {}, {0: 0})
        with self.assertRaisesRegex(ValueError, "prescribed displacement"):
            solve([0, 1], [Element(0, 1, 1, 1)], {}, {})

    def test_rejects_zero_length_element(self):
        with self.assertRaisesRegex(ValueError, "zero length"):
            solve([0, 0], [Element(0, 1, 1, 1)], {}, {0: 0})

    def test_rejects_overflowing_element_stiffness(self):
        with self.assertRaisesRegex(ValueError, "stiffness"):
            solve([0, 1], [Element(0, 1, 1e308, 1e308)], {}, {0: 0})


if __name__ == "__main__":
    unittest.main()
