"""Testes unitários da interface de linha de comando (CLI)."""

import io
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from lajes_concreto_nbr6118.cli import main


class TestCLI(unittest.TestCase):
    def setUp(self):
        self.exemplo_json = Path(__file__).parent.parent / "examples" / "laje_piso_residencial_cruz.json"

    def test_cli_versao(self):
        with self.assertRaises(SystemExit) as ctx:
            main(["--versao"])
        self.assertEqual(ctx.exception.code, 0)

    def test_cli_ajuda(self):
        with self.assertRaises(SystemExit) as ctx:
            main(["--ajuda"])
        self.assertEqual(ctx.exception.code, 0)

    def test_cli_gerar_exemplo(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            caminho_out = os.path.join(tmp_dir, "exemplo_gerado.json")
            ret = main(["gerar-exemplo", "-o", caminho_out])
            self.assertEqual(ret, 0)
            self.assertTrue(os.path.exists(caminho_out))

    def test_cli_calcular_texto(self):
        f = io.StringIO()
        with patch("sys.stdout", f):
            ret = main(["calcular", str(self.exemplo_json), "-f", "texto"])
        self.assertEqual(ret, 0)
        saida = f.getvalue()
        self.assertIn("MEMORIAL DESCRITIVO DE DIMENSIONAMENTO ESTRUTURAL", saida)

    def test_cli_calcular_json(self):
        f = io.StringIO()
        with patch("sys.stdout", f):
            ret = main(["calcular", str(self.exemplo_json), "-f", "json"])
        self.assertEqual(ret, 0)
        saida = f.getvalue()
        self.assertIn("ABNT NBR 6118:2023", saida)

    def test_cli_calcular_csv_arquivo(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_csv = os.path.join(tmp_dir, "saida.csv")
            ret = main(["calcular", str(self.exemplo_json), "-f", "csv", "-o", out_csv])
            self.assertEqual(ret, 0)
            self.assertTrue(os.path.exists(out_csv))

    def test_cli_calcular_svg_arquivo(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_svg = os.path.join(tmp_dir, "saida.svg")
            ret = main(["calcular", str(self.exemplo_json), "-f", "svg", "-o", out_svg])
            self.assertEqual(ret, 0)
            self.assertTrue(os.path.exists(out_svg))

    def test_cli_calcular_zip_arquivo(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_zip = os.path.join(tmp_dir, "saida.zip")
            ret = main(["calcular", str(self.exemplo_json), "-f", "zip", "-o", out_zip])
            self.assertEqual(ret, 0)
            self.assertTrue(os.path.exists(out_zip))

    def test_cli_verificar_sucesso(self):
        f = io.StringIO()
        with patch("sys.stdout", f):
            ret = main(["verificar", str(self.exemplo_json)])
        self.assertEqual(ret, 0)
        self.assertIn("[CONFORME]", f.getvalue())

    def test_cli_arquivo_inexistente_erro(self):
        f_err = io.StringIO()
        with patch("sys.stderr", f_err):
            ret = main(["calcular", "arquivo_inexistente_12345.json"])
        self.assertEqual(ret, 1)


if __name__ == "__main__":
    unittest.main()
