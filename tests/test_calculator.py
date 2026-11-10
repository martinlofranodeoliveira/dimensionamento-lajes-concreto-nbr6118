"""Testes unitários detalhados das funções de cálculo analítico de lajes."""

from fractions import Fraction
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from lajes_concreto_nbr6118.calculator import (
    calcular_carregamentos,
    calcular_esforcos,
    determinar_tipo_marcus,
    dimensionar_armadura_faixa,
    dimensionar_laje_completa,
    dimensionar_todas_armaduras,
    interpolar_coeficientes_marcus,
    raiz_quadrada_fracao,
    validar_geometria_e_materiais,
    verificar_cisalhamento_v_rd1,
    verificar_els,
)
from lajes_concreto_nbr6118.models import LajeEntrada, VinculacoesBordas


class TestCalculator(unittest.TestCase):
    def test_raiz_quadrada_fracao_casos(self):
        self.assertEqual(raiz_quadrada_fracao(Fraction(0, 1)), Fraction(0, 1))
        self.assertEqual(raiz_quadrada_fracao(Fraction(4, 1)), Fraction(2, 1))
        self.assertEqual(raiz_quadrada_fracao(Fraction(9, 16)), Fraction(3, 4))
        self.assertEqual(raiz_quadrada_fracao(Fraction(100, 49)), Fraction(10, 7))

        r2 = raiz_quadrada_fracao(Fraction(2, 1), precisao_decimais=6)
        self.assertAlmostEqual(float(r2), 1.414213, places=5)

        with self.assertRaises(ValueError):
            raiz_quadrada_fracao(Fraction(-1, 4))

    def test_validar_geometria_erros(self):
        v = VinculacoesBordas("APOIADA", "APOIADA", "APOIADA", "APOIADA")

        # lx <= 0
        with self.assertRaises(ValueError):
            validar_geometria_e_materiais(LajeEntrada("L", Fraction(0, 1), Fraction(4, 1), Fraction(10, 1), "C25", "CAA_II", "PISO_NAO_BALANCO", Fraction(1, 1), Fraction(2, 1), v))

        # lx > ly
        with self.assertRaises(ValueError):
            validar_geometria_e_materiais(LajeEntrada("L", Fraction(5, 1), Fraction(4, 1), Fraction(10, 1), "C25", "CAA_II", "PISO_NAO_BALANCO", Fraction(1, 1), Fraction(2, 1), v))

        # Espessura h menor que a normativa para piso (8 cm)
        with self.assertRaises(ValueError):
            validar_geometria_e_materiais(LajeEntrada("L", Fraction(4, 1), Fraction(5, 1), Fraction(6, 1), "C25", "CAA_II", "PISO_NAO_BALANCO", Fraction(1, 1), Fraction(2, 1), v))

        # Classe de concreto inválida
        with self.assertRaises(ValueError):
            validar_geometria_e_materiais(LajeEntrada("L", Fraction(4, 1), Fraction(5, 1), Fraction(10, 1), "C99", "CAA_II", "PISO_NAO_BALANCO", Fraction(1, 1), Fraction(2, 1), v))

    def test_calcular_carregamentos(self):
        v = VinculacoesBordas("APOIADA", "APOIADA", "APOIADA", "APOIADA")
        entrada = LajeEntrada("L1", Fraction(4, 1), Fraction(5, 1), Fraction(10, 1), "C25", "CAA_II", "PISO_NAO_BALANCO", Fraction(15, 10), Fraction(2, 1), v)
        c = calcular_carregamentos(entrada)

        # h = 10 cm -> g_pp = 25 * 0.10 = 2.5 kN/m²
        self.assertEqual(c.g_peso_proprio_kn_m2, Fraction(25, 10))
        # g_tot = 2.5 + 1.5 = 4.0 kN/m²
        self.assertEqual(c.g_total_kn_m2, Fraction(4, 1))
        # p_servico = 4.0 + 2.0 = 6.0 kN/m²
        self.assertEqual(c.p_servico_kn_m2, Fraction(6, 1))
        # p_calculo = 1.4 * 6.0 = 8.4 kN/m²
        self.assertEqual(c.p_calculo_kn_m2, Fraction(84, 10))

    def test_determinar_tipo_marcus(self):
        # Tipo 1: 0 engastes
        v1 = VinculacoesBordas("APOIADA", "APOIADA", "APOIADA", "APOIADA")
        self.assertEqual(determinar_tipo_marcus(v1), "TIPO_1")

        # Tipo 2A: 1 engaste em x
        v2a = VinculacoesBordas("ENGASTADA", "APOIADA", "APOIADA", "APOIADA")
        self.assertEqual(determinar_tipo_marcus(v2a), "TIPO_2A")

        # Tipo 2B: 1 engaste em y
        v2b = VinculacoesBordas("APOIADA", "APOIADA", "ENGASTADA", "APOIADA")
        self.assertEqual(determinar_tipo_marcus(v2b), "TIPO_2B")

        # Tipo 3: 1 engaste em x e 1 em y (adjacentes)
        v3 = VinculacoesBordas("ENGASTADA", "APOIADA", "ENGASTADA", "APOIADA")
        self.assertEqual(determinar_tipo_marcus(v3), "TIPO_3")

        # Tipo 4A: 2 engastes opostos em x
        v4a = VinculacoesBordas("ENGASTADA", "ENGASTADA", "APOIADA", "APOIADA")
        self.assertEqual(determinar_tipo_marcus(v4a), "TIPO_4A")

        # Tipo 4B: 2 engastes opostos em y
        v4b = VinculacoesBordas("APOIADA", "APOIADA", "ENGASTADA", "ENGASTADA")
        self.assertEqual(determinar_tipo_marcus(v4b), "TIPO_4B")

        # Tipo 5A: 2 engastes em x e 1 em y
        v5a = VinculacoesBordas("ENGASTADA", "ENGASTADA", "ENGASTADA", "APOIADA")
        self.assertEqual(determinar_tipo_marcus(v5a), "TIPO_5A")

        # Tipo 5B: 1 engaste em x e 2 em y
        v5b = VinculacoesBordas("ENGASTADA", "APOIADA", "ENGASTADA", "ENGASTADA")
        self.assertEqual(determinar_tipo_marcus(v5b), "TIPO_5B")

        # Tipo 6: 4 engastes
        v6 = VinculacoesBordas("ENGASTADA", "ENGASTADA", "ENGASTADA", "ENGASTADA")
        self.assertEqual(determinar_tipo_marcus(v6), "TIPO_6")

    def test_interpolar_coeficientes_marcus(self):
        # Exato no ponto 1.0
        c1 = interpolar_coeficientes_marcus("TIPO_1", Fraction(10, 10))
        self.assertEqual(c1["mu_x"], Fraction(367, 100))
        self.assertEqual(c1["mu_y"], Fraction(367, 100))

        # Interpolação no ponto intermediário 1.25
        c_meio = interpolar_coeficientes_marcus("TIPO_1", Fraction(125, 100))
        # Em 1.2 mu_x = 4.95, em 1.3 mu_x = 5.57 -> ponto médio = 5.26
        self.assertEqual(c_meio["mu_x"], Fraction(526, 100))

    def test_calcular_esforcos_cruz_e_unidirecional(self):
        v = VinculacoesBordas("APOIADA", "APOIADA", "APOIADA", "APOIADA")

        # Laje em cruz (4x5, lambda = 1.25 <= 2)
        e_cruz = LajeEntrada("L1", Fraction(4, 1), Fraction(5, 1), Fraction(10, 1), "C25", "CAA_II", "PISO_NAO_BALANCO", Fraction(15, 10), Fraction(2, 1), v)
        c_cruz = calcular_carregamentos(e_cruz)
        esf_cruz = calcular_esforcos(e_cruz, c_cruz)
        self.assertEqual(esf_cruz.tipo_armacao, "CRUZ")
        self.assertGreater(esf_cruz.mxd_kn_m_m, 0)
        self.assertGreater(esf_cruz.myd_kn_m_m, 0)

        # Laje unidirecional (2x5, lambda = 2.5 > 2)
        e_uni = LajeEntrada("L2", Fraction(2, 1), Fraction(5, 1), Fraction(10, 1), "C25", "CAA_II", "PISO_NAO_BALANCO", Fraction(15, 10), Fraction(2, 1), v)
        c_uni = calcular_carregamentos(e_uni)
        esf_uni = calcular_esforcos(e_uni, c_uni)
        self.assertEqual(esf_uni.tipo_armacao, "UNIDIRECIONAL")
        self.assertGreater(esf_uni.mxd_kn_m_m, esf_uni.myd_kn_m_m)

    def test_dimensionar_armadura_faixa_e_ductilidade(self):
        # Faixa com momento moderado
        faixa = dimensionar_armadura_faixa(
            direcao="X_POSITIVA",
            momento_calculo_kn_m_m=Fraction(12, 1),
            d_util_cm=Fraction(75, 10),
            h_cm=Fraction(10, 1),
            fck_classe="C25",
            bitola_mm="8.0",
        )
        self.assertGreater(faixa.as_calculado_cm2_m, 0)
        self.assertGreaterEqual(faixa.as_adotado_cm2_m, faixa.as_minimo_cm2_m)
        self.assertGreaterEqual(faixa.espacamento_adotado_cm, 7)
        self.assertLessEqual(faixa.espacamento_adotado_cm, 20)

        # Momento nulo (deve adotar armadura mínima)
        faixa_zero = dimensionar_armadura_faixa(
            direcao="X_POSITIVA",
            momento_calculo_kn_m_m=Fraction(0, 1),
            d_util_cm=Fraction(75, 10),
            h_cm=Fraction(10, 1),
            fck_classe="C25",
            bitola_mm="8.0",
        )
        self.assertEqual(faixa_zero.as_calculado_cm2_m, Fraction(0, 1))
        self.assertEqual(faixa_zero.as_adotado_cm2_m, faixa_zero.as_minimo_cm2_m)

        # Momento excessivo violando ductilidade mu > 0.2952
        with self.assertRaises(ValueError):
            dimensionar_armadura_faixa(
                direcao="X_POSITIVA",
                momento_calculo_kn_m_m=Fraction(150, 1),  # 150 kN.m/m em laje de 10 cm é gigante
                d_util_cm=Fraction(75, 10),
                h_cm=Fraction(10, 1),
                fck_classe="C25",
                bitola_mm="8.0",
            )

    def test_verificar_cisalhamento_v_rd1(self):
        v = VinculacoesBordas("APOIADA", "APOIADA", "APOIADA", "APOIADA")
        entrada = LajeEntrada("L1", Fraction(4, 1), Fraction(5, 1), Fraction(10, 1), "C25", "CAA_II", "PISO_NAO_BALANCO", Fraction(15, 10), Fraction(2, 1), v)
        c = calcular_carregamentos(entrada)
        esf = calcular_esforcos(entrada, c)
        arms = dimensionar_todas_armaduras(entrada, esf)
        cis = verificar_cisalhamento_v_rd1(entrada, esf, arms)
        self.assertTrue(cis.atende)
        self.assertGreater(cis.vrd1_kn_m, cis.vsd_kn_m)

    def test_dimensionar_laje_completa_sucesso(self):
        v = VinculacoesBordas("APOIADA", "APOIADA", "APOIADA", "APOIADA")
        entrada = LajeEntrada("L1", Fraction(4, 1), Fraction(5, 1), Fraction(10, 1), "C25", "CAA_II", "PISO_NAO_BALANCO", Fraction(15, 10), Fraction(2, 1), v)
        resultado = dimensionar_laje_completa(entrada)
        self.assertTrue(resultado.conformidade_geral)
        self.assertIn("CONFORME COM ABNT NBR 6118:2023", resultado.resumo_executivo)

    def test_laje_com_quatro_bordas_engastadas_tipo6(self):
        v6 = VinculacoesBordas("ENGASTADA", "ENGASTADA", "ENGASTADA", "ENGASTADA")
        entrada = LajeEntrada("L_Engastada", Fraction(4, 1), Fraction(5, 1), Fraction(10, 1), "C30", "CAA_II", "PISO_NAO_BALANCO", Fraction(1, 1), Fraction(2, 1), v6)
        resultado = dimensionar_laje_completa(entrada)
        self.assertEqual(resultado.esforcos.tipo_marcus, "TIPO_6")
        self.assertGreater(resultado.esforcos.mxed_kn_m_m, 0)
        self.assertGreater(resultado.esforcos.myed_kn_m_m, 0)
        self.assertIn("X_NEGATIVA", resultado.armaduras)
        self.assertIn("Y_NEGATIVA", resultado.armaduras)
        self.assertTrue(resultado.conformidade_geral)

    def test_laje_unidirecional_biengastada(self):
        v = VinculacoesBordas("ENGASTADA", "ENGASTADA", "APOIADA", "APOIADA")
        entrada = LajeEntrada("L_Uni_Bieng", Fraction(2, 1), Fraction(6, 1), Fraction(9, 1), "C25", "CAA_I", "PISO_NAO_BALANCO", Fraction(1, 1), Fraction(2, 1), v)
        resultado = dimensionar_laje_completa(entrada)
        self.assertEqual(resultado.esforcos.tipo_armacao, "UNIDIRECIONAL")
        self.assertGreater(resultado.esforcos.mxed_kn_m_m, 0)
        self.assertTrue(resultado.conformidade_geral)

    def test_laje_veiculos_pesados_espessura_minima(self):
        v = VinculacoesBordas("APOIADA", "APOIADA", "APOIADA", "APOIADA")
        # h = 10 cm deve falhar para VEICULOS_PESADOS (mínimo 12 cm)
        with self.assertRaises(ValueError):
            validar_geometria_e_materiais(
                LajeEntrada("L_Garagem", Fraction(4, 1), Fraction(5, 1), Fraction(10, 1), "C30", "CAA_II", "VEICULOS_PESADOS", Fraction(1, 1), Fraction(5, 1), v)
            )
        # h = 12 cm deve passar
        validar_geometria_e_materiais(
            LajeEntrada("L_Garagem", Fraction(4, 1), Fraction(5, 1), Fraction(12, 1), "C30", "CAA_II", "VEICULOS_PESADOS", Fraction(1, 1), Fraction(5, 1), v)
        )

    def test_laje_cobertura_espessura_minima_7cm(self):
        v = VinculacoesBordas("APOIADA", "APOIADA", "APOIADA", "APOIADA")
        # h = 6 cm deve falhar para COBERTURA_NAO_BALANCO (mínimo 7 cm)
        with self.assertRaises(ValueError):
            validar_geometria_e_materiais(
                LajeEntrada("L_Cob", Fraction(3, 1), Fraction(4, 1), Fraction(6, 1), "C25", "CAA_I", "COBERTURA_NAO_BALANCO", Fraction(1, 1), Fraction(1, 1), v)
            )
        # h = 7 cm deve passar
        validar_geometria_e_materiais(
            LajeEntrada("L_Cob", Fraction(3, 1), Fraction(4, 1), Fraction(7, 1), "C25", "CAA_I", "COBERTURA_NAO_BALANCO", Fraction(1, 1), Fraction(1, 1), v)
        )

    def test_cobrimentos_todas_classes(self):
        v = VinculacoesBordas("APOIADA", "APOIADA", "APOIADA", "APOIADA")
        for caa in ("CAA_I", "CAA_II", "CAA_III", "CAA_IV"):
            entrada = LajeEntrada("L_CAA", Fraction(3, 1), Fraction(4, 1), Fraction(12, 1), "C30", caa, "PISO_NAO_BALANCO", Fraction(1, 1), Fraction(2, 1), v)
            validar_geometria_e_materiais(entrada)


if __name__ == "__main__":
    unittest.main()
