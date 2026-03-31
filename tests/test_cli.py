from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from distance_routing import cli


class CliTests(unittest.TestCase):
    """Cobertura de la CLI principal con defaults y opciones explícitas."""

    def test_open_route_uses_explicit_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            input_path = tmp_path / "puntos.txt"
            output_path = tmp_path / "ruta.txt"
            input_path.write_text("0 0 0\n2 0 0\n", encoding="utf-8")

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = cli.main(
                    ["open-route", "--input", str(input_path), "--output", str(output_path)]
                )

            self.assertEqual(exit_code, 0)
            self.assertIn("Ruta abierta mínima", stdout.getvalue())
            self.assertTrue(output_path.exists())

    def test_defaults_can_be_monkeypatched(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            input_path = tmp_path / "puntos.txt"
            output_path = tmp_path / "ruta_abierta.txt"
            input_path.write_text("0 0 0\n2 0 0\n", encoding="utf-8")

            stdout = StringIO()
            with (
                patch.object(cli, "default_input_path", return_value=input_path),
                patch.object(cli, "default_output_path", return_value=output_path),
                redirect_stdout(stdout),
            ):
                exit_code = cli.main(["open-route"])

            self.assertEqual(exit_code, 0)
            self.assertIn("Resultado guardado en", stdout.getvalue())
            self.assertTrue(output_path.exists())

    def test_fixed_y_option_is_applied(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            input_path = Path(tmp_dir) / "puntos.txt"
            input_path.write_text("0 0 0\n2 4 2\n", encoding="utf-8")

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = cli.main(
                    ["warehouse-fixed", "--input", str(input_path), "--fixed-y", "-1"]
                )

            self.assertEqual(exit_code, 0)
            self.assertIn("(1.0, -1.0, 1.0)", stdout.getvalue())

    def test_run_all_generates_all_batch_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            input_path = tmp_path / "puntos.txt"
            output_dir = tmp_path / "out"
            input_path.write_text("0 1 0\n2 2 0\n", encoding="utf-8")

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = cli.main(
                    [
                        "run-all",
                        "--input",
                        str(input_path),
                        "--fixed-y",
                        "0",
                        "--output-dir",
                        str(output_dir),
                    ]
                )

            self.assertEqual(exit_code, 0)
            self.assertIn("Ruta abierta mínima", stdout.getvalue())
            self.assertTrue((output_dir / "ruta_abierta.txt").exists())
            self.assertTrue((output_dir / "ruta_cerrada.txt").exists())
            self.assertTrue((output_dir / "solucion_bodega_mst.txt").exists())
            self.assertTrue((output_dir / "solucion_bodega_monotona_y.txt").exists())


if __name__ == "__main__":
    unittest.main()
