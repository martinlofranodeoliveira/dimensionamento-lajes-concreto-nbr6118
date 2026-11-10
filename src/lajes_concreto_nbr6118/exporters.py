"""Exportadores de dados, relatórios e pacotes determinísticos para lajes maciças.

Padrões de engenharia LOFRANO TECNOLOGIA:
- Sanitização contra injeção de fórmulas em CSV (prefixo "'" para '=', '+', '-', '@', '\\t', '\\r').
- Empacotamento ZIP determinístico com timestamp fixo (2026, 1, 1, 0, 0, 0) e flags de não-sobrescrita.
- Relatório técnico estruturado em conformidade com a ABNT NBR 6118:2023.
"""

from __future__ import annotations

import csv
from fractions import Fraction
import io
import os
from pathlib import Path
import zipfile

from .codecs import resultado_para_dict
from .models import ResultadoLaje

DATA_HORA_DETERMINISTICA_ZIP = (2026, 1, 1, 0, 0, 0)


def sanitizar_campo_csv(valor: object) -> str:
    """Sanitiza strings contra ataques de injeção de fórmulas em planilhas."""
    texto = str(valor)
    if texto and texto[0] in ("=", "+", "-", "@", "\t", "\r"):
        return f"'{texto}"
    return texto


def exportar_relatorio_texto(resultado: ResultadoLaje) -> str:
    """Gera relatório de cálculo técnico formatado em texto legível para memorial descritivo."""
    e = resultado.entrada
    c = resultado.carregamentos
    esf = resultado.esforcos
    cis = resultado.cisalhamento
    els = resultado.els

    linhas = [
        "=" * 82,
        "   LOFRANO TECNOLOGIA — MEMORIAL DESCRITIVO DE DIMENSIONAMENTO ESTRUTURAL",
        "             LAJES MACIÇAS DE CONCRETO ARMADO (ABNT NBR 6118:2023)",
        "=" * 82,
        f"Laje Identificador:        {e.identificador}",
        f"Tipo de Uso:               {e.tipo_uso}",
        f"Classe de Agressividade:   {e.classe_agressividade} (Cobrimento c_nom = {float(els.cobrimento_cm):.1f} cm)",
        f"Classe do Concreto:        {e.fck_classe} (f_ck = {float(e.fck_classe[1:]):.0f} MPa)",
        f"Aço Estrutural:            CA-50 (f_yk = 500 MPa, f_yd = 434.78 MPa)",
        "-" * 82,
        "1. GEOMETRIA DA LAJE E CONDIÇÕES DE CONTORNO",
        f"  Menor Vão Livre (lx):    {float(e.lx_m):.2f} m",
        f"  Maior Vão Livre (ly):    {float(e.ly_m):.2f} m",
        f"  Relação de Forma (ly/lx): {float(esf.lambda_relacao):.2f} -> Classificação: {esf.tipo_armacao}",
        f"  Tipo de Contorno Marcus: {esf.tipo_marcus}",
        f"  Espessura Adotada (h):   {float(e.h_cm):.1f} cm",
        f"  Vinculações das Bordas:  x0={e.vinculacoes.borda_x0}, x1={e.vinculacoes.borda_x1}, y0={e.vinculacoes.borda_y0}, y1={e.vinculacoes.borda_y1}",
        "-" * 82,
        "2. AÇÕES E CARREGAMENTOS (kN/m²)",
        f"  Peso Próprio (g_pp):     {float(c.g_peso_proprio_kn_m2):.2f} kN/m²",
        f"  Carga Permanente Adic.:  {float(e.g_adicional_kn_m2):.2f} kN/m²",
        f"  Carga Permanente Total:  {float(c.g_total_kn_m2):.2f} kN/m²",
        f"  Sobrecarga de Uso (q):   {float(c.q_servico_kn_m2):.2f} kN/m²",
        f"  Carga de Serviço (p_k):  {float(c.p_servico_kn_m2):.2f} kN/m²",
        f"  Carga de Cálculo (p_d):  {float(c.p_calculo_kn_m2):.2f} kN/m² (Majorador gamma_f = 1.40)",
        "-" * 82,
        "3. ESFORÇOS SOLICITANTES DE CÁLCULO (ELU)",
        f"  Momento Positivo X (mxd): {float(esf.mxd_kn_m_m):.2f} kN.m/m (mx_k = {float(esf.mx_k_kn_m_m):.2f} kN.m/m)",
        f"  Momento Positivo Y (myd): {float(esf.myd_kn_m_m):.2f} kN.m/m (my_k = {float(esf.my_k_kn_m_m):.2f} kN.m/m)",
        f"  Momento Negativo X (mxed):{float(esf.mxed_kn_m_m):.2f} kN.m/m",
        f"  Momento Negativo Y (myed):{float(esf.myed_kn_m_m):.2f} kN.m/m",
        f"  Reação de Apoio Linear X: {float(esf.vx_kn_m):.2f} kN/m",
        f"  Reação de Apoio Linear Y: {float(esf.vy_kn_m):.2f} kN/m",
        "-" * 82,
        "4. DETALHAMENTO DAS ARMADURAS DE FLEXÃO (Faixa Unitária de 100 cm)",
    ]

    for chave, a in resultado.armaduras.items():
        linhas.extend([
            f"  * Direção {chave}:",
            f"      Momento de Cálculo:  {float(a.momento_calculo_kn_m_m):.2f} kN.m/m",
            f"      Altura Útil (d):     {float(a.d_util_cm):.2f} cm",
            f"      As Calculado:        {float(a.as_calculado_cm2_m):.2f} cm²/m",
            f"      As Mínimo Normativo: {float(a.as_minimo_cm2_m):.2f} cm²/m",
            f"      As Adotado:          {float(a.as_adotado_cm2_m):.2f} cm²/m",
            f"      Detalhamento:        Bitola {a.bitola_mm} mm c/ {a.espacamento_adotado_cm} cm ({a.numero_barras_por_metro} barras/m)",
            f"      As Efetivo:          {float(a.as_efetivo_cm2_m):.2f} cm²/m",
        ])

    linhas.extend([
        "-" * 82,
        "5. VERIFICAÇÃO DA FORÇA CORTANTE SEM ARMADURA TRANSVERSAL (V_Rd1)",
        f"  Cortante Solicitante Máx (V_sd): {float(cis.vsd_kn_m):.2f} kN/m",
        f"  Cortante Resistente (V_Rd1):     {float(cis.vrd1_kn_m):.2f} kN/m",
        f"  Taxa de Solicitação (Vsd/VRd1):  {float(cis.ratio_solicitacao) * 100:.1f}%",
        f"  Diagnóstico de Cisalhamento:     {'APROVADO' if cis.atende else 'REPROVADO'}",
        f"  Laudo: {cis.mensagem}",
        "-" * 82,
        "6. ESTADOS LIMITES DE SERVIÇO (ELS)",
        f"  Flecha Imediata em Serviço:      {float(els.flecha_imediata_cm):.3f} cm",
        f"  Flecha Diferida no Tempo (alpha=2): {float(els.flecha_diferida_cm):.3f} cm",
        f"  Flecha Total em Serviço:         {float(els.flecha_total_cm):.3f} cm",
        f"  Flecha Limite Normativa (lx/250):{float(els.flecha_limite_cm):.3f} cm",
        f"  Verificação de Deformação (ELS): {'CONFORME' if els.atende_flecha else 'NÃO CONFORME'}",
        f"  Abertura de Fissuras Estimada:   {float(els.abertura_fissura_estimada_mm):.2f} mm",
        f"  Abertura de Fissuras Limite:     {float(els.abertura_fissura_limite_mm):.2f} mm",
        f"  Verificação de Fissuração:       {'CONFORME' if els.atende_fissura else 'NÃO CONFORME'}",
        "-" * 82,
        "7. CONCLUSÃO GERAL DE ENGENHARIA",
        f"  Parecer Estrutural: {'APROVADO E EM CONFORMIDADE' if resultado.conformidade_geral else 'NÃO CONFORME'}",
        f"  Resumo Executivo:   {resultado.resumo_executivo}",
        "=" * 82,
    ])

    return "\n".join(linhas) + "\n"


def exportar_csv(resultado: ResultadoLaje, caminho_destino: str | Path) -> None:
    """Exporta métricas de cálculo para arquivo CSV protegido contra injeção de fórmulas."""
    e = resultado.entrada
    c = resultado.carregamentos
    esf = resultado.esforcos
    cis = resultado.cisalhamento
    els = resultado.els

    with open(caminho_destino, "w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f, delimiter=";", quoting=csv.QUOTE_MINIMAL)

        escritor.writerow([
            sanitizar_campo_csv("parametro"),
            sanitizar_campo_csv("unidade"),
            sanitizar_campo_csv("valor_numerico"),
            sanitizar_campo_csv("fracao_racional"),
            sanitizar_campo_csv("status_normativo"),
        ])

        linhas_dados = [
            ("identificador", "-", e.identificador, "-", "OK"),
            ("lx_m", "m", f"{float(e.lx_m):.2f}", f"{e.lx_m.numerator}/{e.lx_m.denominator}", "OK"),
            ("ly_m", "m", f"{float(e.ly_m):.2f}", f"{e.ly_m.numerator}/{e.ly_m.denominator}", "OK"),
            ("lambda_forma", "-", f"{float(esf.lambda_relacao):.2f}", f"{esf.lambda_relacao.numerator}/{esf.lambda_relacao.denominator}", esf.tipo_armacao),
            ("espessura_h", "cm", f"{float(e.h_cm):.1f}", f"{e.h_cm.numerator}/{e.h_cm.denominator}", "OK"),
            ("fck_classe", "MPa", e.fck_classe, "-", "OK"),
            ("g_total", "kN/m2", f"{float(c.g_total_kn_m2):.2f}", f"{c.g_total_kn_m2.numerator}/{c.g_total_kn_m2.denominator}", "OK"),
            ("q_servico", "kN/m2", f"{float(c.q_servico_kn_m2):.2f}", f"{c.q_servico_kn_m2.numerator}/{c.q_servico_kn_m2.denominator}", "OK"),
            ("p_calculo_pd", "kN/m2", f"{float(c.p_calculo_kn_m2):.2f}", f"{c.p_calculo_kn_m2.numerator}/{c.p_calculo_kn_m2.denominator}", "OK"),
            ("momento_mxd", "kN.m/m", f"{float(esf.mxd_kn_m_m):.2f}", f"{esf.mxd_kn_m_m.numerator}/{esf.mxd_kn_m_m.denominator}", "OK"),
            ("momento_myd", "kN.m/m", f"{float(esf.myd_kn_m_m):.2f}", f"{esf.myd_kn_m_m.numerator}/{esf.myd_kn_m_m.denominator}", "OK"),
            ("cortante_vsd", "kN/m", f"{float(cis.vsd_kn_m):.2f}", f"{cis.vsd_kn_m.numerator}/{cis.vsd_kn_m.denominator}", "OK"),
            ("cortante_vrd1", "kN/m", f"{float(cis.vrd1_kn_m):.2f}", f"{cis.vrd1_kn_m.numerator}/{cis.vrd1_kn_m.denominator}", "OK"),
            ("ratio_cisalhamento", "-", f"{float(cis.ratio_solicitacao):.4f}", f"{cis.ratio_solicitacao.numerator}/{cis.ratio_solicitacao.denominator}", "CONFORME" if cis.atende else "FALHA"),
            ("flecha_total", "cm", f"{float(els.flecha_total_cm):.3f}", f"{els.flecha_total_cm.numerator}/{els.flecha_total_cm.denominator}", "OK"),
            ("flecha_limite", "cm", f"{float(els.flecha_limite_cm):.3f}", f"{els.flecha_limite_cm.numerator}/{els.flecha_limite_cm.denominator}", "CONFORME" if els.atende_flecha else "FALHA"),
            ("conformidade_geral", "-", "1" if resultado.conformidade_geral else "0", "-", "APROVADO" if resultado.conformidade_geral else "REPROVADO"),
        ]

        for p, u, vn, fr, st in linhas_dados:
            escritor.writerow([
                sanitizar_campo_csv(p),
                sanitizar_campo_csv(u),
                sanitizar_campo_csv(vn),
                sanitizar_campo_csv(fr),
                sanitizar_campo_csv(st),
            ])


def exportar_zip_deterministico(
    resultado: ResultadoLaje,
    caminho_zip: str | Path,
    conteudo_svg: str | None = None,
) -> None:
    """Cria um pacote ZIP determinístico com modo não-sobrescrita e timestamps normalizados."""
    caminho = Path(caminho_zip)
    if caminho.exists():
        raise FileExistsError(f"Arquivo de destino já existe e não será sobrescrito: {caminho}")

    # Criação do arquivo com proteção atômica
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    if hasattr(os, "O_BINARY"):
        flags |= os.O_BINARY

    fd = os.open(str(caminho), flags, 0o644)
    with os.fdopen(fd, "wb") as f_out:
        with zipfile.ZipFile(f_out, "w", zipfile.ZIP_DEFLATED) as zf:
            # 1. Relatório técnico em texto
            relatorio = exportar_relatorio_texto(resultado)
            info_txt = zipfile.ZipInfo("memorial_calculo.txt", DATA_HORA_DETERMINISTICA_ZIP)
            info_txt.external_attr = 0o644 << 16
            zf.writestr(info_txt, relatorio.encode("utf-8"))

            # 2. Dados em JSON canônico
            dados_dict = resultado_para_dict(resultado)
            import json
            json_str = json.dumps(dados_dict, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
            info_json = zipfile.ZipInfo("resultado_calculo.json", DATA_HORA_DETERMINISTICA_ZIP)
            info_json.external_attr = 0o644 << 16
            zf.writestr(info_json, json_str.encode("utf-8"))

            # 3. Planilha CSV sanitizada
            buffer_csv = io.StringIO()
            escritor = csv.writer(buffer_csv, delimiter=";", quoting=csv.QUOTE_MINIMAL)
            escritor.writerow([sanitizar_campo_csv("parametro"), sanitizar_campo_csv("valor")])
            escritor.writerow([sanitizar_campo_csv("identificador"), sanitizar_campo_csv(resultado.entrada.identificador)])
            escritor.writerow([sanitizar_campo_csv("tipo_armacao"), sanitizar_campo_csv(resultado.esforcos.tipo_armacao)])
            escritor.writerow([sanitizar_campo_csv("conformidade"), sanitizar_campo_csv(resultado.conformidade_geral)])
            info_csv = zipfile.ZipInfo("resumo_dados.csv", DATA_HORA_DETERMINISTICA_ZIP)
            info_csv.external_attr = 0o644 << 16
            zf.writestr(info_csv, buffer_csv.getvalue().encode("utf-8"))

            # 4. Painel SVG técnico (se fornecido)
            if conteudo_svg is not None:
                info_svg = zipfile.ZipInfo("painel_detalhamento.svg", DATA_HORA_DETERMINISTICA_ZIP)
                info_svg.external_attr = 0o644 << 16
                zf.writestr(info_svg, conteudo_svg.encode("utf-8"))
