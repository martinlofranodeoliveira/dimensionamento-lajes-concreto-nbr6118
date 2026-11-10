"""Interface de linha de comando (CLI) para dimensionamento de lajes maciças (ABNT NBR 6118:2023).

Fornece comandos completos em português com saída em múltiplos formatos (texto, json, csv, svg, zip)
e proteção de codificação para execução multiplataforma no Linux e Windows.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import json
import os
from pathlib import Path
import sys

from .calculator import dimensionar_laje_completa
from .codecs import (
    carregar_json_canonico,
    entrada_de_dict,
    resultado_para_dict,
    salvar_json_canonico,
)
from .exporters import (
    exportar_csv,
    exportar_relatorio_texto,
    exportar_zip_deterministico,
)
from .models import LajeEntrada, VinculacoesBordas
from .svg_generator import gerar_painel_svg

__version__ = "1.0.0"


def _configurar_stdout_seguro() -> None:
    """Garante que a saída padrão suporte UTF-8 sem falhar sob codificação legada no Windows."""
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
        except Exception:
            pass
    if hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")
        except Exception:
            pass


def _criar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lajes-concreto",
        description="Dimensionamento e verificação analítica de lajes maciças de concreto armado (ABNT NBR 6118:2023).",
        add_help=False,
    )

    parser.add_argument("-h", "--help", "--ajuda", action="help", help="Exibe esta mensagem de ajuda e sai.")
    parser.add_argument("-v", "--version", "--versao", action="version", version=f"%(prog)s {__version__}", help="Exibe a versão do programa e sai.")

    subparsers = parser.add_subparsers(dest="comando", help="Comandos disponíveis")

    # Subcomando 'calcular'
    p_calc = subparsers.add_parser("calcular", help="Dimensiona e verifica uma laje a partir de arquivo JSON de entrada.", add_help=False)
    p_calc.add_argument("-h", "--help", "--ajuda", action="help", help="Ajuda do comando calcular.")
    p_calc.add_argument("arquivo_entrada", help="Caminho do arquivo JSON canônico com os dados da laje.")
    p_calc.add_argument(
        "-f", "--formato",
        choices=["texto", "json", "csv", "svg", "zip"],
        default="texto",
        help="Formato da saída gerada (padrão: texto).",
    )
    p_calc.add_argument("-o", "--saida", help="Caminho do arquivo de saída (opcional para texto/json; obrigatório para zip).")

    # Subcomando 'verificar'
    p_ver = subparsers.add_parser("verificar", help="Verifica a conformidade normativa de uma laje e retorna código de saída 0 ou 1.", add_help=False)
    p_ver.add_argument("-h", "--help", "--ajuda", action="help", help="Ajuda do comando verificar.")
    p_ver.add_argument("arquivo_entrada", help="Caminho do arquivo JSON de entrada.")

    # Subcomando 'gerar-exemplo'
    p_ex = subparsers.add_parser("gerar-exemplo", help="Gera um modelo de arquivo JSON canônico de entrada.", add_help=False)
    p_ex.add_argument("-h", "--help", "--ajuda", action="help", help="Ajuda do comando gerar-exemplo.")
    p_ex.add_argument("-o", "--saida", default="laje_exemplo.json", help="Caminho do arquivo de destino (padrão: laje_exemplo.json).")

    return parser


def comando_calcular(args: argparse.Namespace) -> int:
    try:
        dados_json = carregar_json_canonico(args.arquivo_entrada)
        entrada = entrada_de_dict(dados_json)
        resultado = dimensionar_laje_completa(entrada)
    except Exception as exc:
        print(f"Erro no processamento da laje: {exc}", file=sys.stderr)
        return 1

    formato = args.formato
    saida = args.saida

    if formato == "texto":
        relatorio = exportar_relatorio_texto(resultado)
        if saida:
            with open(saida, "w", encoding="utf-8") as f:
                f.write(relatorio)
            print(f"Relatório salvo em: {saida}")
        else:
            print(relatorio)
    elif formato == "json":
        if saida:
            salvar_json_canonico(resultado, saida)
            print(f"Resultado JSON salvo em: {saida}")
        else:
            dados = resultado_para_dict(resultado)
            print(json.dumps(dados, indent=2, ensure_ascii=False, sort_keys=True))
    elif formato == "csv":
        if not saida:
            saida = "resultado_laje.csv"
        exportar_csv(resultado, saida)
        print(f"Planilha CSV salva em: {saida}")
    elif formato == "svg":
        if not saida:
            saida = "painel_laje.svg"
        conteudo_svg = gerar_painel_svg(resultado)
        with open(saida, "w", encoding="utf-8") as f:
            f.write(conteudo_svg)
        print(f"Painel vetorial SVG salvo em: {saida}")
    elif formato == "zip":
        if not saida:
            saida = f"laje_{entrada.identificador}_pacote.zip"
        conteudo_svg = gerar_painel_svg(resultado)
        exportar_zip_deterministico(resultado, saida, conteudo_svg=conteudo_svg)
        print(f"Pacote determinístico ZIP salvo em: {saida}")

    return 0 if resultado.conformidade_geral else 2


def comando_verificar(args: argparse.Namespace) -> int:
    try:
        dados_json = carregar_json_canonico(args.arquivo_entrada)
        entrada = entrada_de_dict(dados_json)
        resultado = dimensionar_laje_completa(entrada)
    except Exception as exc:
        print(f"Erro de validação: {exc}", file=sys.stderr)
        return 1

    if resultado.conformidade_geral:
        print(f"[CONFORME] Laje '{entrada.identificador}' atende a todos os critérios da ABNT NBR 6118:2023.")
        print(f"           {resultado.resumo_executivo}")
        return 0
    else:
        print(f"[NÃO CONFORME] Laje '{entrada.identificador}' apresenta não-conformidades estruturais.")
        print(f"               {resultado.resumo_executivo}", file=sys.stderr)
        return 1


def comando_gerar_exemplo(args: argparse.Namespace) -> int:
    exemplo = {
        "identificador": "L1",
        "lx_m": "4.0",
        "ly_m": "5.0",
        "h_cm": "10.0",
        "fck_classe": "C25",
        "classe_agressividade": "CAA_II",
        "tipo_uso": "PISO_NAO_BALANCO",
        "g_adicional_kn_m2": "1.5",
        "q_acidental_kn_m2": "2.0",
        "vinculacoes": {
            "borda_x0": "APOIADA",
            "borda_x1": "APOIADA",
            "borda_y0": "APOIADA",
            "borda_y1": "APOIADA",
        },
        "bitola_x_mm": "8.0",
        "bitola_y_mm": "8.0",
        "bitola_engaste_mm": "10.0",
    }
    with open(args.saida, "w", encoding="utf-8") as f:
        json.dump(exemplo, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"Modelo JSON de laje gerado com sucesso em: {args.saida}")
    return 0


def main(argv: list[str] | None = None) -> int:
    _configurar_stdout_seguro()
    parser = _criar_parser()
    args = parser.parse_args(argv)

    if not args.comando:
        parser.print_help()
        return 0

    if args.comando == "calcular":
        return comando_calcular(args)
    elif args.comando == "verificar":
        return comando_verificar(args)
    elif args.comando == "gerar-exemplo":
        return comando_gerar_exemplo(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
