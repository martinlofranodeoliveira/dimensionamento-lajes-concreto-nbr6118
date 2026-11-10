"""Testes unitários das constantes e tabelas normativas (ABNT NBR 6118:2023)."""

from fractions import Fraction
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from lajes_concreto_nbr6118.constants import (
    ABERTURAS_MAXIMAS_FISSURAS_MM,
    ARMADURA_SECUNDARIA_MINIMA_ABSOLUTA_CM2_M,
    BITOLAS_COMERCIAIS_LAJES,
    CLASSES_CONCRETO_F_CK,
    COBRIMENTOS_NOMINAIS_CM,
    ESPACAMENTO_MAXIMO_PRINCIPAL_ABSOLUTO_CM,
    ESPACAMENTO_MAXIMO_SECUNDARIA_ABSOLUTO_CM,
    ESPACAMENTO_MINIMO_ABSOLUTO_CM,
    ESPESSURAS_MINIMAS_USO_CM,
    F_YD_CA50_KN_CM2,
    F_YK_CA50_KN_CM2,
    GAMMA_C,
    GAMMA_F,
    GAMMA_S,
    LARGURA_FAIXA_CALCULO_CM,
    MODULO_ELASTICIDADE_ACO_KN_CM2,
    PESO_ESPECIFICO_CONCRETO_ARMADO,
    TABELA_MARCUS_COEFICIENTES,
    TAXAS_MINIMAS_ARMADURA_RHO,
)


class TestConstants(unittest.TestCase):
    def test_coeficientes_ponderacao_racionais(self):
        self.assertEqual(GAMMA_C, Fraction(14, 10))
        self.assertEqual(GAMMA_S, Fraction(115, 100))
        self.assertEqual(GAMMA_F, Fraction(14, 10))
        self.assertEqual(PESO_ESPECIFICO_CONCRETO_ARMADO, Fraction(25, 1))
        self.assertEqual(LARGURA_FAIXA_CALCULO_CM, Fraction(100, 1))

    def test_propriedades_aco_ca50(self):
        self.assertEqual(F_YK_CA50_KN_CM2, Fraction(50, 1))
        self.assertEqual(F_YD_CA50_KN_CM2, Fraction(1000, 23))
        self.assertEqual(MODULO_ELASTICIDADE_ACO_KN_CM2, Fraction(21000, 1))

    def test_classes_concreto_fck(self):
        self.assertIn("C20", CLASSES_CONCRETO_F_CK)
        self.assertIn("C25", CLASSES_CONCRETO_F_CK)
        self.assertIn("C30", CLASSES_CONCRETO_F_CK)
        self.assertIn("C50", CLASSES_CONCRETO_F_CK)
        self.assertEqual(CLASSES_CONCRETO_F_CK["C25"], Fraction(25, 10))
        self.assertEqual(CLASSES_CONCRETO_F_CK["C30"], Fraction(30, 10))

    def test_taxas_minimas_armadura(self):
        self.assertEqual(TAXAS_MINIMAS_ARMADURA_RHO["C20"], Fraction(150, 100000))
        self.assertEqual(TAXAS_MINIMAS_ARMADURA_RHO["C25"], Fraction(150, 100000))
        self.assertEqual(TAXAS_MINIMAS_ARMADURA_RHO["C30"], Fraction(150, 100000))
        self.assertEqual(TAXAS_MINIMAS_ARMADURA_RHO["C35"], Fraction(164, 100000))

    def test_cobrimentos_e_aberturas_fissuras(self):
        self.assertEqual(COBRIMENTOS_NOMINAIS_CM["CAA_I"], Fraction(20, 10))
        self.assertEqual(COBRIMENTOS_NOMINAIS_CM["CAA_II"], Fraction(25, 10))
        self.assertEqual(COBRIMENTOS_NOMINAIS_CM["CAA_III"], Fraction(35, 10))
        self.assertEqual(ABERTURAS_MAXIMAS_FISSURAS_MM["CAA_I"], Fraction(4, 10))
        self.assertEqual(ABERTURAS_MAXIMAS_FISSURAS_MM["CAA_II"], Fraction(3, 10))

    def test_espessuras_minimas_normativas(self):
        self.assertEqual(ESPESSURAS_MINIMAS_USO_CM["COBERTURA_NAO_BALANCO"], Fraction(7, 1))
        self.assertEqual(ESPESSURAS_MINIMAS_USO_CM["PISO_NAO_BALANCO"], Fraction(8, 1))
        self.assertEqual(ESPESSURAS_MINIMAS_USO_CM["BALANCO_PISO"], Fraction(10, 1))
        self.assertEqual(ESPESSURAS_MINIMAS_USO_CM["VEICULOS_PESADOS"], Fraction(12, 1))

    def test_bitolas_comerciais(self):
        for bitola in ("5.0", "6.3", "8.0", "10.0", "12.5"):
            self.assertIn(bitola, BITOLAS_COMERCIAIS_LAJES)
            dados = BITOLAS_COMERCIAIS_LAJES[bitola]
            self.assertGreater(dados["diametro_mm"], 0)
            self.assertGreater(dados["area_cm2"], 0)

    def test_espacamentos_limites(self):
        self.assertEqual(ESPACAMENTO_MINIMO_ABSOLUTO_CM, Fraction(7, 1))
        self.assertEqual(ESPACAMENTO_MAXIMO_PRINCIPAL_ABSOLUTO_CM, Fraction(20, 1))
        self.assertEqual(ESPACAMENTO_MAXIMO_SECUNDARIA_ABSOLUTO_CM, Fraction(33, 1))
        self.assertEqual(ARMADURA_SECUNDARIA_MINIMA_ABSOLUTA_CM2_M, Fraction(9, 10))

    def test_tabela_marcus_tipos_e_pontos(self):
        tipos_esperados = ["TIPO_1", "TIPO_2A", "TIPO_2B", "TIPO_3", "TIPO_4A", "TIPO_4B", "TIPO_5A", "TIPO_5B", "TIPO_6"]
        for t in tipos_esperados:
            self.assertIn(t, TABELA_MARCUS_COEFICIENTES)
            tabela = TABELA_MARCUS_COEFICIENTES[t]
            self.assertIn(Fraction(10, 10), tabela)
            self.assertIn(Fraction(20, 10), tabela)
            self.assertEqual(len(tabela), 11)  # de 1.0 a 2.0 em passos de 0.1


if __name__ == "__main__":
    unittest.main()
