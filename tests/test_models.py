"""Testes unitários dos modelos de dados de lajes maciças."""

from fractions import Fraction
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from lajes_concreto_nbr6118.models import (
    ArmaduraFaixa,
    CarregamentosLaje,
    EsforcosLaje,
    LajeEntrada,
    ResultadoLaje,
    VerificacaoCisalhamento,
    VerificacaoELS,
    VinculacoesBordas,
)


class TestModels(unittest.TestCase):
    def test_vinculacoes_bordas_contagens(self):
        v = VinculacoesBordas(
            borda_x0="ENGASTADA",
            borda_x1="APOIADA",
            borda_y0="APOIADA",
            borda_y1="LIVRE",
        )
        self.assertEqual(v.total_engastes(), 1)
        self.assertEqual(v.total_apoios(), 2)
        self.assertEqual(v.total_livres(), 1)

    def test_laje_entrada_imutavel(self):
        v = VinculacoesBordas("APOIADA", "APOIADA", "APOIADA", "APOIADA")
        entrada = LajeEntrada(
            identificador="L1",
            lx_m=Fraction(4, 1),
            ly_m=Fraction(5, 1),
            h_cm=Fraction(10, 1),
            fck_classe="C25",
            classe_agressividade="CAA_II",
            tipo_uso="PISO_NAO_BALANCO",
            g_adicional_kn_m2=Fraction(15, 10),
            q_acidental_kn_m2=Fraction(2, 1),
            vinculacoes=v,
        )
        self.assertEqual(entrada.identificador, "L1")
        self.assertEqual(entrada.lx_m, Fraction(4, 1))
        with self.assertRaises(Exception):
            entrada.h_cm = Fraction(12, 1)  # type: ignore

    def test_armadura_faixa_imutavel(self):
        faixa = ArmaduraFaixa(
            direcao="X_POSITIVA",
            momento_calculo_kn_m_m=Fraction(10, 1),
            d_util_cm=Fraction(7, 1),
            as_calculado_cm2_m=Fraction(3, 1),
            as_minimo_cm2_m=Fraction(15, 10),
            as_adotado_cm2_m=Fraction(3, 1),
            bitola_mm="8.0",
            espacamento_calculado_cm=Fraction(16, 1),
            espacamento_adotado_cm=16,
            numero_barras_por_metro=7,
            as_efetivo_cm2_m=Fraction(35, 10),
        )
        self.assertEqual(faixa.direcao, "X_POSITIVA")
        self.assertEqual(faixa.numero_barras_por_metro, 7)
        with self.assertRaises(Exception):
            faixa.espacamento_adotado_cm = 15  # type: ignore


if __name__ == "__main__":
    unittest.main()
