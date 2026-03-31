from pathlib import Path
import tempfile
import unittest

from distance_routing.io_utils import read_points_txt


class ReadPointsTxtTests(unittest.TestCase):
    """Casos de validación de lectura del archivo de puntos."""

    def test_accepts_valid_rows_and_skips_empty_lines(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            input_path = Path(tmp_dir) / "puntos.txt"
            input_path.write_text("0 0 0\n\n1.5 2 3\n", encoding="utf-8")

            points = read_points_txt(input_path)

            self.assertEqual(points, [(0.0, 0.0, 0.0), (1.5, 2.0, 3.0)])

    def test_rejects_bad_columns(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            input_path = Path(tmp_dir) / "puntos.txt"
            input_path.write_text("1 2\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "se esperaban 3 valores"):
                read_points_txt(input_path)

    def test_rejects_empty_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            input_path = Path(tmp_dir) / "puntos.txt"
            input_path.write_text("\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "no contiene puntos"):
                read_points_txt(input_path)


if __name__ == "__main__":
    unittest.main()
