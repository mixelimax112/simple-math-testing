import unittest
from simple_math import SimpleMath


class TestSimpleMath(unittest.TestCase):
    def setUp(self):
        self.math = SimpleMath()

    def test_square_positive(self):
        """Тест метода square с положительным числом."""
        self.assertEqual(self.math.square(2), 4)

    def test_square_negative(self):
        """Тест метода square с отрицательным числом."""
        self.assertEqual(self.math.square(-3), 9)

    def test_square_zero(self):
        """Тест метода square с нулём."""
        self.assertEqual(self.math.square(0), 0)

    def test_cube_positive(self):
        """Тест метода cube с положительным числом."""
        self.assertEqual(self.math.cube(3), 27)

    def test_cube_negative(self):
        """Тест метода cube с отрицательным числом."""
        self.assertEqual(self.math.cube(-3), -27)

    def test_cube_zero(self):
        """Тест метода cube с нулём."""
        self.assertEqual(self.math.cube(0), 0)


if __name__ == '__main__':
    unittest.main()
