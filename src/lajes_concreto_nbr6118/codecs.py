"""Módulo de codificação e decodificação canônica JSON para dimensionamento de lajes.

Padrão rigoroso LOFRANO TECNOLOGIA:
- Rejeição absoluta de BOM (\\xef\\xbb\\xbf ou \\ufeff).
- Rejeição absoluta de tipos de ponto flutuante (float) no payload de entrada.
- Rejeição de chaves duplicadas.
- Limite de profundidade de aninhamento recursivo (máximo 32).
- Serialização determinística com ordenação alfabética e indentação uniforme.
"""

from __future__ import annotations

from fractions import Fraction
import json
import os
from pathlib import Path
from typing import Any

from .models import (
    ArmaduraFaixa,
    CarregamentosLaje,
    EsforcosLaje,
    LajeEntrada,
    ResultadoLaje,
    VerificacaoCisalhamento,
    VerificacaoELS,
    VinculacoesBordas,
)

PROFUNDIDADE_MAXIMA_JSON = 32


def _rejeitar_float(token: str) -> None:
    raise ValueError(
        f"Ponto flutuante proibido na entrada canônica: '{token}'. "
        f"Forneça grandezas em inteiros ou razões exatas (ex: string '2.5' ou inteiros)."
    )


def _verificar_pares_sem_duplicacao(pares: list[tuple[str, Any]]) -> dict[str, Any]:
    chaves_vistas = set()
    dicionario = {}
    for chave, valor in pares:
        if chave in chaves_vistas:
            raise ValueError(f"Chave duplicada detectada no JSON canônico: '{chave}'")
        chaves_vistas.add(chave)
        dicionario[chave] = valor
    return dicionario


def _verificar_profundidade(obj: Any, nivel_atual: int = 0) -> None:
    if nivel_atual > PROFUNDIDADE_MAXIMA_JSON:
        raise ValueError(
            f"Profundidade JSON excedeu o limite máximo seguro de {PROFUNDIDADE_MAXIMA_JSON} níveis."
        )
    if isinstance(obj, dict):
        for v in obj.values():
            _verificar_profundidade(v, nivel_atual + 1)
    elif isinstance(obj, list):
        for item in obj:
            _verificar_profundidade(item, nivel_atual + 1)


def parsear_fracao(valor: Any) -> Fraction:
    """Converte inteiros, strings ou dicts racionais em Fraction exata."""
    if isinstance(valor, Fraction):
        return valor
    if isinstance(valor, int):
        return Fraction(valor, 1)
    if isinstance(valor, str):
        # Aceita formatos "4", "4/5", "4.5", "4,5"
        v_limpo = valor.strip().replace(",", ".")
        if "/" in v_limpo:
            partes = v_limpo.split("/")
            if len(partes) == 2:
                return Fraction(int(partes[0].strip()), int(partes[1].strip()))
        return Fraction(v_limpo)
    if isinstance(valor, dict) and "numerador" in valor and "denominador" in valor:
        return Fraction(int(valor["numerador"]), int(valor["denominador"]))
    raise ValueError(f"Não foi possível converter '{valor}' ({type(valor).__name__}) em Fraction exata.")


def fracao_para_dict(f: Fraction) -> dict[str, Any]:
    """Converte uma Fraction em estrutura legível canônica."""
    return {
        "numerador": f.numerator,
        "denominador": f.denominator,
        "valor_decimal": f"{float(f):.6f}",
    }


def carregar_json_canonico(caminho_ou_conteudo: str | Path) -> dict[str, Any]:
    """Carrega dados JSON validando ausência de BOM, ausência de floats e integridade."""
    if isinstance(caminho_ou_conteudo, (str, Path)) and os.path.exists(str(caminho_ou_conteudo)):
        with open(caminho_ou_conteudo, "rb") as f:
            bytes_conteudo = f.read()
    elif isinstance(caminho_ou_conteudo, str):
        bytes_conteudo = caminho_ou_conteudo.encode("utf-8")
    else:
        raise ValueError("Entrada inválida para carregar_json_canonico.")

    # Rejeição estrita de Byte Order Mark (BOM) UTF-8
    if bytes_conteudo.startswith(b"\xef\xbb\xbf"):
        raise ValueError("Byte Order Mark (BOM) UTF-8 detectado e estritamente proibido.")

    texto = bytes_conteudo.decode("utf-8")
    if "\ufeff" in texto:
        raise ValueError("Caractere BOM detectado no corpo do texto e estritamente proibido.")

    dados = json.loads(
        texto,
        parse_float=_rejeitar_float,
        object_pairs_hook=_verificar_pares_sem_duplicacao,
    )
    _verificar_profundidade(dados)
    return dados


def entrada_de_dict(dados: dict[str, Any]) -> LajeEntrada:
    """Reconstitui um objeto LajeEntrada a partir de um dicionário validado."""
    vinc_dict = dados.get("vinculacoes", {})
    vinculacoes = VinculacoesBordas(
        borda_x0=vinc_dict.get("borda_x0", "APOIADA"),
        borda_x1=vinc_dict.get("borda_x1", "APOIADA"),
        borda_y0=vinc_dict.get("borda_y0", "APOIADA"),
        borda_y1=vinc_dict.get("borda_y1", "APOIADA"),
    )

    return LajeEntrada(
        identificador=str(dados.get("identificador", "L1")),
        lx_m=parsear_fracao(dados["lx_m"]),
        ly_m=parsear_fracao(dados["ly_m"]),
        h_cm=parsear_fracao(dados["h_cm"]),
        fck_classe=str(dados.get("fck_classe", "C25")),
        classe_agressividade=str(dados.get("classe_agressividade", "CAA_II")),
        tipo_uso=str(dados.get("tipo_uso", "PISO_NAO_BALANCO")),
        g_adicional_kn_m2=parsear_fracao(dados.get("g_adicional_kn_m2", 1)),
        q_acidental_kn_m2=parsear_fracao(dados.get("q_acidental_kn_m2", 2)),
        vinculacoes=vinculacoes,
        bitola_x_mm=str(dados.get("bitola_x_mm", "8.0")),
        bitola_y_mm=str(dados.get("bitola_y_mm", "8.0")),
        bitola_engaste_mm=str(dados.get("bitola_engaste_mm", "10.0")),
    )


def resultado_para_dict(resultado: ResultadoLaje) -> dict[str, Any]:
    """Serializa o resultado completo em dicionário canônico com valores racionais e decimais."""
    e = resultado.entrada
    c = resultado.carregamentos
    esf = resultado.esforcos
    cis = resultado.cisalhamento
    els = resultado.els

    armaduras_dict = {}
    for k, a in resultado.armaduras.items():
        armaduras_dict[k] = {
            "direcao": a.direcao,
            "momento_calculo_kn_m_m": fracao_para_dict(a.momento_calculo_kn_m_m),
            "d_util_cm": fracao_para_dict(a.d_util_cm),
            "as_calculado_cm2_m": fracao_para_dict(a.as_calculado_cm2_m),
            "as_minimo_cm2_m": fracao_para_dict(a.as_minimo_cm2_m),
            "as_adotado_cm2_m": fracao_para_dict(a.as_adotado_cm2_m),
            "bitola_mm": a.bitola_mm,
            "espacamento_calculado_cm": fracao_para_dict(a.espacamento_calculado_cm),
            "espacamento_adotado_cm": a.espacamento_adotado_cm,
            "numero_barras_por_metro": a.numero_barras_por_metro,
            "as_efetivo_cm2_m": fracao_para_dict(a.as_efetivo_cm2_m),
        }

    return {
        "norma_referencia": "ABNT NBR 6118:2023",
        "entrada": {
            "identificador": e.identificador,
            "lx_m": fracao_para_dict(e.lx_m),
            "ly_m": fracao_para_dict(e.ly_m),
            "h_cm": fracao_para_dict(e.h_cm),
            "fck_classe": e.fck_classe,
            "classe_agressividade": e.classe_agressividade,
            "tipo_uso": e.tipo_uso,
            "g_adicional_kn_m2": fracao_para_dict(e.g_adicional_kn_m2),
            "q_acidental_kn_m2": fracao_para_dict(e.q_acidental_kn_m2),
            "vinculacoes": {
                "borda_x0": e.vinculacoes.borda_x0,
                "borda_x1": e.vinculacoes.borda_x1,
                "borda_y0": e.vinculacoes.borda_y0,
                "borda_y1": e.vinculacoes.borda_y1,
            },
            "bitola_x_mm": e.bitola_x_mm,
            "bitola_y_mm": e.bitola_y_mm,
            "bitola_engaste_mm": e.bitola_engaste_mm,
        },
        "carregamentos": {
            "g_peso_proprio_kn_m2": fracao_para_dict(c.g_peso_proprio_kn_m2),
            "g_total_kn_m2": fracao_para_dict(c.g_total_kn_m2),
            "q_servico_kn_m2": fracao_para_dict(c.q_servico_kn_m2),
            "p_servico_kn_m2": fracao_para_dict(c.p_servico_kn_m2),
            "p_calculo_kn_m2": fracao_para_dict(c.p_calculo_kn_m2),
        },
        "esforcos": {
            "lambda_relacao": fracao_para_dict(esf.lambda_relacao),
            "tipo_armacao": esf.tipo_armacao,
            "tipo_marcus": esf.tipo_marcus,
            "mx_k_kn_m_m": fracao_para_dict(esf.mx_k_kn_m_m),
            "my_k_kn_m_m": fracao_para_dict(esf.my_k_kn_m_m),
            "mxe_k_kn_m_m": fracao_para_dict(esf.mxe_k_kn_m_m),
            "mye_k_kn_m_m": fracao_para_dict(esf.mye_k_kn_m_m),
            "mxd_kn_m_m": fracao_para_dict(esf.mxd_kn_m_m),
            "myd_kn_m_m": fracao_para_dict(esf.myd_kn_m_m),
            "mxed_kn_m_m": fracao_para_dict(esf.mxed_kn_m_m),
            "myed_kn_m_m": fracao_para_dict(esf.myed_kn_m_m),
            "vx_kn_m": fracao_para_dict(esf.vx_kn_m),
            "vy_kn_m": fracao_para_dict(esf.vy_kn_m),
        },
        "armaduras": armaduras_dict,
        "cisalhamento_v_rd1": {
            "vsd_kn_m": fracao_para_dict(cis.vsd_kn_m),
            "vrd1_kn_m": fracao_para_dict(cis.vrd1_kn_m),
            "ratio_solicitacao": fracao_para_dict(cis.ratio_solicitacao),
            "atende": cis.atende,
            "mensagem": cis.mensagem,
        },
        "verificacao_els": {
            "cobrimento_cm": fracao_para_dict(els.cobrimento_cm),
            "flecha_imediata_cm": fracao_para_dict(els.flecha_imediata_cm),
            "flecha_diferida_cm": fracao_para_dict(els.flecha_diferida_cm),
            "flecha_total_cm": fracao_para_dict(els.flecha_total_cm),
            "flecha_limite_cm": fracao_para_dict(els.flecha_limite_cm),
            "atende_flecha": els.atende_flecha,
            "abertura_fissura_estimada_mm": fracao_para_dict(els.abertura_fissura_estimada_mm),
            "abertura_fissura_limite_mm": fracao_para_dict(els.abertura_fissura_limite_mm),
            "atende_fissura": els.atende_fissura,
        },
        "conformidade_geral": resultado.conformidade_geral,
        "resumo_executivo": resultado.resumo_executivo,
    }


def salvar_json_canonico(resultado: ResultadoLaje, caminho_destino: str | Path) -> None:
    """Salva os resultados em arquivo JSON canônico com codificação UTF-8 sem BOM."""
    dados = resultado_para_dict(resultado)
    conteudo = json.dumps(dados, indent=2, ensure_ascii=False, sort_keys=True)
    with open(caminho_destino, "w", encoding="utf-8") as f:
        f.write(conteudo)
        f.write("\n")
