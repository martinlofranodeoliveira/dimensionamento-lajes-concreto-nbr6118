"""Testes unitários da geração do painel técnico SVG."""

from fractions import Fraction
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from lajes_concreto_nbr6118.calculator import dimensionar_laje_completa
from lajes_concreto_nbr6118.models import LajeEntrada, VinculacoesBordas
from lajes_concreto_nbr6118.svg_generator import ALTURA_CANVAS, LARGURA_CANVAS, gerar_painel_svg


class TestSVGGenerator(unittest.TestCase):
    def test_gerar_painel_svg_estrutura(self):
        v = VinculacoesBordas("APOIADA", "APOIADA", "APOIADA", "APOIADA")
        entrada = LajeEntrada("L1_Teste", Fraction(4, 1), Fraction(5, 1), Fraction(10, 1), "C25", "CAA_II", "PISO_NAO_BALANCO", Fraction(15, 10), Fraction(2, 1), v)
        resultado = dimensionar_laje_completa(entrada)

        svg = gerar_painel_svg(resultado)
        self.assertTrue(svg.startswith("<svg"))
        self.assertTrue(svg.strip().endswith("</svg>"))
        self.assertIn(f'viewBox="0 0 {LARGURA_CANVAS} {ALTURA_CANVAS}"', svg)
        self.assertIn("LOFRANO TECNOLOGIA", svg)
        self.assertIn("DIMENSIONAMENTO DE LAJES MACIÇAS", svg)
        self.assertIn("ABNT NBR 6118:2023", svg)
        self.assertIn("Laje L1_Teste", svg)
        self.assertIn("CONFORME NBR 6118:2023", svg)

    def test_gerar_painel_svg_unidirecional(self):
        v = VinculacoesBordas("ENGASTADA", "APOIADA", "APOIADA", "APOIADA")
        entrada = LajeEntrada("L2_Uni", Fraction(24, 10), Fraction(6, 1), Fraction(9, 1), "C30", "CAA_II", "PISO_NAO_BALANCO", Fraction(12, 10), Fraction(3, 1), v)
        resultado = dimensionar_laje_completa(entrada)

        svg = gerar_painel_svg(resultado)
        self.assertIn("UNIDIRECIONAL", svg)
        self.assertIn("C30", svg)


if __name__ == "__main__":
    unittest.main()
