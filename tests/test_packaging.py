"""Testes unitários de conformidade do empacotamento e exportações do módulo."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import lajes_concreto_nbr6118


class TestPackaging(unittest.TestCase):
    def test_versao_consistente(self):
        self.assertEqual(lajes_concreto_nbr6118.__version__, "1.0.0")

    def test_marcador_py_typed_presente(self):
        pacote_dir = Path(lajes_concreto_nbr6118.__file__).parent
        py_typed = pacote_dir / "py.typed"
        self.assertTrue(py_typed.exists(), "Marcador py.typed ausente no pacote.")

    def test_exportacoes_em_all(self):
        for simbolo in lajes_concreto_nbr6118.__all__:
            self.assertTrue(
                hasattr(lajes_concreto_nbr6118, simbolo),
                f"Símbolo '{simbolo}' declarado em __all__ mas não encontrado no pacote.",
            )

    def test_pyproject_toml_presente(self):
        raiz = Path(lajes_concreto_nbr6118.__file__).parent.parent.parent
        pyproject = raiz / "pyproject.toml"
        self.assertTrue(pyproject.exists(), "pyproject.toml não encontrado na raiz.")
        conteudo = pyproject.read_text(encoding="utf-8")
        self.assertIn('name = "dimensionamento-lajes-concreto-nbr6118"', conteudo)
        self.assertIn('version = "1.0.0"', conteudo)
        self.assertIn('lajes-concreto = "lajes_concreto_nbr6118.cli:main"', conteudo)


if __name__ == "__main__":
    unittest.main()
