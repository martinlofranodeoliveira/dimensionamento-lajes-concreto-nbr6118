"""Testes unitários dos exportadores de dados e proteção CSV/ZIP."""

from fractions import Fraction
import os
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from lajes_concreto_nbr6118.calculator import dimensionar_laje_completa
from lajes_concreto_nbr6118.exporters import (
    DATA_HORA_DETERMINISTICA_ZIP,
    exportar_csv,
    exportar_relatorio_texto,
    exportar_zip_deterministico,
    sanitizar_campo_csv,
)
from lajes_concreto_nbr6118.models import LajeEntrada, VinculacoesBordas


class TestExporters(unittest.TestCase):
    def test_sanitizar_campo_csv(self):
        self.assertEqual(sanitizar_campo_csv("=1+1"), "'=1+1")
        self.assertEqual(sanitizar_campo_csv("+cmd"), "'+cmd")
        self.assertEqual(sanitizar_campo_csv("-10"), "'-10")
        self.assertEqual(sanitizar_campo_csv("@SUM(A1)"), "'@SUM(A1)")
        self.assertEqual(sanitizar_campo_csv("\ttab"), "'\ttab")
        self.assertEqual(sanitizar_campo_csv("\rret"), "'\rret")
        self.assertEqual(sanitizar_campo_csv("Texto Seguro"), "Texto Seguro")
        self.assertEqual(sanitizar_campo_csv(123), "123")

    def test_exportar_relatorio_texto(self):
        v = VinculacoesBordas("APOIADA", "APOIADA", "APOIADA", "APOIADA")
        entrada = LajeEntrada("L1", Fraction(4, 1), Fraction(5, 1), Fraction(10, 1), "C25", "CAA_II", "PISO_NAO_BALANCO", Fraction(15, 10), Fraction(2, 1), v)
        resultado = dimensionar_laje_completa(entrada)
        texto = exportar_relatorio_texto(resultado)

        self.assertIn("MEMORIAL DESCRITIVO DE DIMENSIONAMENTO ESTRUTURAL", texto)
        self.assertIn("ABNT NBR 6118:2023", texto)
        self.assertIn("Laje Identificador:        L1", texto)
        self.assertIn("1. GEOMETRIA DA LAJE E CONDIÇÕES DE CONTORNO", texto)
        self.assertIn("5. VERIFICAÇÃO DA FORÇA CORTANTE SEM ARMADURA TRANSVERSAL", texto)
        self.assertIn("6. ESTADOS LIMITES DE SERVIÇO (ELS)", texto)

    def test_exportar_csv(self):
        v = VinculacoesBordas("APOIADA", "APOIADA", "APOIADA", "APOIADA")
        entrada = LajeEntrada("L1", Fraction(4, 1), Fraction(5, 1), Fraction(10, 1), "C25", "CAA_II", "PISO_NAO_BALANCO", Fraction(15, 10), Fraction(2, 1), v)
        resultado = dimensionar_laje_completa(entrada)

        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as tmp:
            caminho_csv = tmp.name
        try:
            exportar_csv(resultado, caminho_csv)
            with open(caminho_csv, "r", encoding="utf-8") as f:
                linhas = f.readlines()
            self.assertGreater(len(linhas), 5)
            self.assertTrue(any("identificador" in l and "L1" in l for l in linhas))
        finally:
            if os.path.exists(caminho_csv):
                os.remove(caminho_csv)

    def test_exportar_zip_deterministico(self):
        v = VinculacoesBordas("APOIADA", "APOIADA", "APOIADA", "APOIADA")
        entrada = LajeEntrada("L1", Fraction(4, 1), Fraction(5, 1), Fraction(10, 1), "C25", "CAA_II", "PISO_NAO_BALANCO", Fraction(15, 10), Fraction(2, 1), v)
        resultado = dimensionar_laje_completa(entrada)

        with tempfile.TemporaryDirectory() as tmp_dir:
            caminho_zip = os.path.join(tmp_dir, "pacote_laje.zip")
            exportar_zip_deterministico(resultado, caminho_zip, conteudo_svg="<svg></svg>")

            self.assertTrue(os.path.exists(caminho_zip))
            with zipfile.ZipFile(caminho_zip, "r") as zf:
                nomes = zf.namelist()
                self.assertIn("memorial_calculo.txt", nomes)
                self.assertIn("resultado_calculo.json", nomes)
                self.assertIn("resumo_dados.csv", nomes)
                self.assertIn("painel_detalhamento.svg", nomes)

                # Verificar timestamp determinístico
                for info in zf.infolist():
                    self.assertEqual(info.date_time, DATA_HORA_DETERMINISTICA_ZIP)

            # Verificar proteção contra sobrescrita não-atômica
            with self.assertRaises(FileExistsError):
                exportar_zip_deterministico(resultado, caminho_zip)


if __name__ == "__main__":
    unittest.main()
