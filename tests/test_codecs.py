"""Testes unitários dos codecs canônicos JSON e proteção contra violações."""

from fractions import Fraction
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from lajes_concreto_nbr6118.calculator import dimensionar_laje_completa
from lajes_concreto_nbr6118.codecs import (
    carregar_json_canonico,
    entrada_de_dict,
    fracao_para_dict,
    parsear_fracao,
    resultado_para_dict,
    salvar_json_canonico,
)
from lajes_concreto_nbr6118.models import LajeEntrada, VinculacoesBordas


class TestCodecs(unittest.TestCase):
    def test_parsear_fracao(self):
        self.assertEqual(parsear_fracao(5), Fraction(5, 1))
        self.assertEqual(parsear_fracao("4"), Fraction(4, 1))
        self.assertEqual(parsear_fracao("3/4"), Fraction(3, 4))
        self.assertEqual(parsear_fracao("2.5"), Fraction(5, 2))
        self.assertEqual(parsear_fracao("2,5"), Fraction(5, 2))
        self.assertEqual(parsear_fracao({"numerador": 7, "denominador": 8}), Fraction(7, 8))
        self.assertEqual(parsear_fracao(Fraction(1, 3)), Fraction(1, 3))

        with self.assertRaises(ValueError):
            parsear_fracao([1, 2])

    def test_fracao_para_dict(self):
        f = Fraction(3, 2)
        d = fracao_para_dict(f)
        self.assertEqual(d["numerador"], 3)
        self.assertEqual(d["denominador"], 2)
        self.assertEqual(d["valor_decimal"], "1.500000")

    def test_rejeitar_bom_bytes(self):
        conteudo = b"\xef\xbb\xbf{\"identificador\": \"L1\"}"
        with tempfile.NamedTemporaryFile("wb", delete=False) as tmp:
            tmp.write(conteudo)
            caminho = tmp.name
        try:
            with self.assertRaises(ValueError) as ctx:
                carregar_json_canonico(caminho)
            self.assertIn("BOM", str(ctx.exception))
        finally:
            if os.path.exists(caminho):
                os.remove(caminho)

    def test_rejeitar_bom_caractere_texto(self):
        texto = "\ufeff{\"identificador\": \"L1\"}"
        with self.assertRaises(ValueError) as ctx:
            carregar_json_canonico(texto)
        self.assertIn("BOM", str(ctx.exception))

    def test_rejeitar_float_direto(self):
        # Números de ponto flutuante diretos no JSON violam o padrão canônico
        json_com_float = '{"lx_m": 4.5, "ly_m": 5}'
        with self.assertRaises(ValueError) as ctx:
            carregar_json_canonico(json_com_float)
        self.assertIn("Ponto flutuante proibido", str(ctx.exception))

    def test_rejeitar_chaves_duplicadas(self):
        json_duplicado = '{"lx_m": "4.0", "lx_m": "5.0"}'
        with self.assertRaises(ValueError) as ctx:
            carregar_json_canonico(json_duplicado)
        self.assertIn("Chave duplicada", str(ctx.exception))

    def test_rejeitar_profundidade_excessiva(self):
        # Montar JSON com profundidade 35 (> 32)
        aninhado = {}
        curr = aninhado
        for _ in range(35):
            curr["filho"] = {}
            curr = curr["filho"]
        json_profundo = json.dumps(aninhado)

        with self.assertRaises(ValueError) as ctx:
            carregar_json_canonico(json_profundo)
        self.assertIn("Profundidade JSON excedeu", str(ctx.exception))

    def test_rejeitar_entrada_invalida_no_carregar_json(self):
        with self.assertRaises(ValueError):
            carregar_json_canonico(12345)  # type: ignore

    def test_entrada_de_dict_defaults(self):
        dados_minimos = {
            "lx_m": "3.0",
            "ly_m": "4.0",
            "h_cm": "8.0",
        }
        entrada = entrada_de_dict(dados_minimos)
        self.assertEqual(entrada.identificador, "L1")
        self.assertEqual(entrada.fck_classe, "C25")
        self.assertEqual(entrada.classe_agressividade, "CAA_II")
        self.assertEqual(entrada.bitola_x_mm, "8.0")
        self.assertEqual(entrada.bitola_y_mm, "8.0")
        self.assertEqual(entrada.vinculacoes.borda_x0, "APOIADA")


if __name__ == "__main__":
    unittest.main()
