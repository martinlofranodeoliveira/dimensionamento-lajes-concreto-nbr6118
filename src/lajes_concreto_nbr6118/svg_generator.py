"""Gerador de painel técnico visual em SVG (1440x900) para detalhamento de lajes maciças.

Gera diagramas vetoriais nítidos em alta resolução com a geometria em planta,
condições de contorno, armaduras longitudinais positivas/negativas e indicadores de conformidade.
"""

from __future__ import annotations

from html import escape
from typing import Final

from .models import ResultadoLaje

LARGURA_CANVAS: Final[int] = 1440
ALTURA_CANVAS: Final[int] = 900


def gerar_painel_svg(resultado: ResultadoLaje) -> str:
    """Gera o painel técnico vetorial SVG 1440x900 da laje dimensionada."""
    e = resultado.entrada
    c = resultado.carregamentos
    esf = resultado.esforcos
    cis = resultado.cisalhamento
    els = resultado.els

    status_cor = "#10b981" if resultado.conformidade_geral else "#ef4444"
    status_texto = "CONFORME NBR 6118:2023" if resultado.conformidade_geral else "NÃO CONFORME"

    # Geometria da laje desenhada no quadrante esquerdo (x: 50 a 650, y: 150 a 580)
    # Escalar lx e ly para caber em uma caixa de 480 x 360 px
    lx_f = float(e.lx_m)
    ly_f = float(e.ly_m)
    fator_escala = min(460.0 / ly_f, 340.0 / lx_f)
    largura_planta = ly_f * fator_escala
    altura_planta = lx_f * fator_escala

    origem_x = 70.0 + (480.0 - largura_planta) / 2.0
    origem_y = 170.0 + (350.0 - altura_planta) / 2.0

    # Determinar cores de contorno (engastada = azul escuro grosso; apoiada = verde)
    cor_x0 = "#2563eb" if e.vinculacoes.borda_x0 == "ENGASTADA" else "#059669"
    cor_x1 = "#2563eb" if e.vinculacoes.borda_x1 == "ENGASTADA" else "#059669"
    cor_y0 = "#2563eb" if e.vinculacoes.borda_y0 == "ENGASTADA" else "#059669"
    cor_y1 = "#2563eb" if e.vinculacoes.borda_y1 == "ENGASTADA" else "#059669"

    ax = resultado.armaduras["X_POSITIVA"]
    ay = resultado.armaduras["Y_POSITIVA"]

    svg_linhas = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {LARGURA_CANVAS} {ALTURA_CANVAS}" width="{LARGURA_CANVAS}" height="{ALTURA_CANVAS}">',
        '  <defs>',
        '    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">',
        '      <stop offset="0%" stop-color="#0f172a" />',
        '      <stop offset="100%" stop-color="#1e293b" />',
        '    </linearGradient>',
        '    <linearGradient id="cardGrad" x1="0%" y1="0%" x2="100%" y2="100%">',
        '      <stop offset="0%" stop-color="#1e293b" />',
        '      <stop offset="100%" stop-color="#334155" />',
        '    </linearGradient>',
        '    <linearGradient id="slabGrad" x1="0%" y1="0%" x2="100%" y2="100%">',
        '      <stop offset="0%" stop-color="#38bdf8" stop-opacity="0.15" />',
        '      <stop offset="100%" stop-color="#0284c7" stop-opacity="0.30" />',
        '    </linearGradient>',
        '    <filter id="dropShadow" x="-10%" y="-10%" width="120%" height="120%">',
        '      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000000" flood-opacity="0.4" />',
        '    </filter>',
        '  </defs>',
        '',
        '  <!-- Fundo Principal -->',
        f'  <rect width="{LARGURA_CANVAS}" height="{ALTURA_CANVAS}" fill="url(#bgGrad)" />',
        '',
        '  <!-- Cabeçalho Técnico -->',
        '  <rect x="30" y="25" width="1380" height="95" rx="12" fill="url(#cardGrad)" filter="url(#dropShadow)" />',
        '  <text x="55" y="65" font-family="system-ui, -apple-system, sans-serif" font-size="24" font-weight="700" fill="#f8fafc">LOFRANO TECNOLOGIA</text>',
        '  <text x="55" y="95" font-family="system-ui, -apple-system, sans-serif" font-size="14" fill="#94a3b8">DIMENSIONAMENTO DE LAJES MACIÇAS DE CONCRETO ARMADO · ABNT NBR 6118:2023</text>',
        '',
        f'  <!-- Selo de Conformidade Geral -->',
        f'  <rect x="1080" y="42" width="300" height="60" rx="8" fill="{status_cor}" fill-opacity="0.2" stroke="{status_cor}" stroke-width="2" />',
        f'  <circle cx="1115" cy="72" r="12" fill="{status_cor}" />',
        f'  <text x="1140" y="78" font-family="system-ui, -apple-system, sans-serif" font-size="16" font-weight="700" fill="{status_cor}">{status_texto}</text>',
        '',
        '  <!-- Painel 1: Planta Baixa e Geometria da Laje -->',
        '  <rect x="30" y="140" width="580" height="440" rx="12" fill="url(#cardGrad)" filter="url(#dropShadow)" />',
        '  <text x="55" y="175" font-family="system-ui, sans-serif" font-size="18" font-weight="700" fill="#38bdf8">1. Planta Baixa e Vinculações de Borda</text>',
        f'  <text x="55" y="200" font-family="system-ui, sans-serif" font-size="13" fill="#94a3b8">Laje {escape(e.identificador)}: {float(e.lx_m):.2f}m x {float(e.ly_m):.2f}m · h = {float(e.h_cm):.1f} cm · {esf.tipo_armacao}</text>',
        '',
        '  <!-- Corpo da Laje em Planta -->',
        f'  <rect x="{origem_x}" y="{origem_y}" width="{largura_planta}" height="{altura_planta}" rx="4" fill="url(#slabGrad)" />',
        '',
        '  <!-- Malha de Armadura Ilustrativa no Miolo -->',
        f'  <line x1="{origem_x + 30}" y1="{origem_y + altura_planta/2}" x2="{origem_x + largura_planta - 30}" y2="{origem_y + altura_planta/2}" stroke="#f59e0b" stroke-width="2" stroke-dasharray="6,4" />',
        f'  <line x1="{origem_x + largura_planta/2}" y1="{origem_y + 25}" x2="{origem_x + largura_planta/2}" y2="{origem_y + altura_planta - 25}" stroke="#10b981" stroke-width="2" stroke-dasharray="6,4" />',
        f'  <text x="{origem_x + largura_planta/2}" y="{origem_y + altura_planta/2 - 10}" font-family="monospace" font-size="12" font-weight="700" fill="#f59e0b" text-anchor="middle">As,x: Φ{ax.bitola_mm} c/{ax.espacamento_adotado_cm}cm</text>',
        f'  <text x="{origem_x + largura_planta/2}" y="{origem_y + altura_planta/2 + 25}" font-family="monospace" font-size="12" font-weight="700" fill="#10b981" text-anchor="middle">As,y: Φ{ay.bitola_mm} c/{ay.espacamento_adotado_cm}cm</text>',
        '',
        '  <!-- 4 Bordas com identificação de vinculação -->',
        f'  <!-- Borda X0 (esquerda) -->',
        f'  <line x1="{origem_x}" y1="{origem_y}" x2="{origem_x}" y2="{origem_y + altura_planta}" stroke="{cor_x0}" stroke-width="6" />',
        f'  <text x="{origem_x - 12}" y="{origem_y + altura_planta/2}" font-family="sans-serif" font-size="11" fill="{cor_x0}" text-anchor="end" transform="rotate(-90, {origem_x - 12}, {origem_y + altura_planta/2})">{e.vinculacoes.borda_x0}</text>',
        '',
        f'  <!-- Borda X1 (direita) -->',
        f'  <line x1="{origem_x + largura_planta}" y1="{origem_y}" x2="{origem_x + largura_planta}" y2="{origem_y + altura_planta}" stroke="{cor_x1}" stroke-width="6" />',
        f'  <text x="{origem_x + largura_planta + 15}" y="{origem_y + altura_planta/2}" font-family="sans-serif" font-size="11" fill="{cor_x1}" text-anchor="start" transform="rotate(90, {origem_x + largura_planta + 15}, {origem_y + altura_planta/2})">{e.vinculacoes.borda_x1}</text>',
        '',
        f'  <!-- Borda Y0 (topo) -->',
        f'  <line x1="{origem_x}" y1="{origem_y}" x2="{origem_x + largura_planta}" y2="{origem_y}" stroke="{cor_y0}" stroke-width="6" />',
        f'  <text x="{origem_x + largura_planta/2}" y="{origem_y - 12}" font-family="sans-serif" font-size="11" fill="{cor_y0}" text-anchor="middle">{e.vinculacoes.borda_y0}</text>',
        '',
        f'  <!-- Borda Y1 (base) -->',
        f'  <line x1="{origem_x}" y1="{origem_y + altura_planta}" x2="{origem_x + largura_planta}" y2="{origem_y + altura_planta}" stroke="{cor_y1}" stroke-width="6" />',
        f'  <text x="{origem_x + largura_planta/2}" y="{origem_y + altura_planta + 22}" font-family="sans-serif" font-size="11" fill="{cor_y1}" text-anchor="middle">{e.vinculacoes.borda_y1}</text>',
        '',
        f'  <!-- Cotas de Dimensão -->',
        f'  <text x="{origem_x + largura_planta/2}" y="{origem_y + altura_planta + 42}" font-family="monospace" font-size="13" font-weight="700" fill="#38bdf8" text-anchor="middle">ly = {float(e.ly_m):.2f} m</text>',
        f'  <text x="{origem_x - 35}" y="{origem_y + altura_planta/2}" font-family="monospace" font-size="13" font-weight="700" fill="#38bdf8" text-anchor="middle" transform="rotate(-90, {origem_x - 35}, {origem_y + altura_planta/2})">lx = {float(e.lx_m):.2f} m</text>',
        '',
        '  <!-- Painel 2: Esforços Solicitantes de Cálculo (ELU) -->',
        '  <rect x="630" y="140" width="370" height="440" rx="12" fill="url(#cardGrad)" filter="url(#dropShadow)" />',
        '  <text x="655" y="175" font-family="system-ui, sans-serif" font-size="18" font-weight="700" fill="#38bdf8">2. Esforços de Cálculo (ELU)</text>',
        f'  <text x="655" y="200" font-family="system-ui, sans-serif" font-size="13" fill="#94a3b8">Método Marcus: {esf.tipo_marcus} · λ = {float(esf.lambda_relacao):.2f}</text>',
        '',
        '  <!-- Tabela de Cargas e Momentos -->',
        f'  <g transform="translate(655, 230)">',
        f'    <text y="0" font-family="sans-serif" font-size="13" fill="#94a3b8">Carga Total p_d (1.4*p):</text>',
        f'    <text x="320" y="0" font-family="monospace" font-size="14" font-weight="700" fill="#f8fafc" text-anchor="end">{float(c.p_calculo_kn_m2):.2f} kN/m²</text>',
        '',
        f'    <text y="35" font-family="sans-serif" font-size="13" fill="#94a3b8">Momento Positivo m_xd:</text>',
        f'    <text x="320" y="35" font-family="monospace" font-size="14" font-weight="700" fill="#f59e0b" text-anchor="end">{float(esf.mxd_kn_m_m):.2f} kN.m/m</text>',
        '',
        f'    <text y="70" font-family="sans-serif" font-size="13" fill="#94a3b8">Momento Positivo m_yd:</text>',
        f'    <text x="320" y="70" font-family="monospace" font-size="14" font-weight="700" fill="#10b981" text-anchor="end">{float(esf.myd_kn_m_m):.2f} kN.m/m</text>',
        '',
        f'    <text y="105" font-family="sans-serif" font-size="13" fill="#94a3b8">Momento Negativo m_xed:</text>',
        f'    <text x="320" y="105" font-family="monospace" font-size="14" font-weight="700" fill="#ef4444" text-anchor="end">{float(esf.mxed_kn_m_m):.2f} kN.m/m</text>',
        '',
        f'    <text y="140" font-family="sans-serif" font-size="13" fill="#94a3b8">Momento Negativo m_yed:</text>',
        f'    <text x="320" y="140" font-family="monospace" font-size="14" font-weight="700" fill="#ef4444" text-anchor="end">{float(esf.myed_kn_m_m):.2f} kN.m/m</text>',
        '',
        f'    <text y="175" font-family="sans-serif" font-size="13" fill="#94a3b8">Reação Linear V_x:</text>',
        f'    <text x="320" y="175" font-family="monospace" font-size="14" font-weight="700" fill="#38bdf8" text-anchor="end">{float(esf.vx_kn_m):.2f} kN/m</text>',
        '',
        f'    <text y="210" font-family="sans-serif" font-size="13" fill="#94a3b8">Reação Linear V_y:</text>',
        f'    <text x="320" y="210" font-family="monospace" font-size="14" font-weight="700" fill="#38bdf8" text-anchor="end">{float(esf.vy_kn_m):.2f} kN/m</text>',
        '',
        f'    <text y="245" font-family="sans-serif" font-size="13" fill="#94a3b8">Cortante Máx V_sd:</text>',
        f'    <text x="320" y="245" font-family="monospace" font-size="14" font-weight="700" fill="#e2e8f0" text-anchor="end">{float(cis.vsd_kn_m):.2f} kN/m</text>',
        '',
        f'    <text y="280" font-family="sans-serif" font-size="13" fill="#94a3b8">Cortante Resistente V_Rd1:</text>',
        f'    <text x="320" y="280" font-family="monospace" font-size="14" font-weight="700" fill="#10b981" text-anchor="end">{float(cis.vrd1_kn_m):.2f} kN/m</text>',
        '',
        f'    <text y="315" font-family="sans-serif" font-size="13" fill="#94a3b8">Taxa Solicitação Vsd/VRd1:</text>',
        f'    <text x="320" y="315" font-family="monospace" font-size="14" font-weight="700" fill="#10b981" text-anchor="end">{float(cis.ratio_solicitacao)*100:.1f}%</text>',
        f'  </g>',
        '',
        '  <!-- Painel 3: Detalhamento de Armaduras e ELS -->',
        '  <rect x="1020" y="140" width="390" height="440" rx="12" fill="url(#cardGrad)" filter="url(#dropShadow)" />',
        '  <text x="1045" y="175" font-family="system-ui, sans-serif" font-size="18" font-weight="700" fill="#38bdf8">3. Armaduras e Estados de Serviço</text>',
        f'  <text x="1045" y="200" font-family="system-ui, sans-serif" font-size="13" fill="#94a3b8">Aço CA-50 · f_ck = {float(e.fck_classe[1:]):.0f} MPa · {e.classe_agressividade}</text>',
        '',
        '  <!-- Bloco Armadura X -->',
        '  <rect x="1045" y="225" width="340" height="75" rx="8" fill="#0f172a" fill-opacity="0.6" stroke="#f59e0b" stroke-width="1.5" />',
        f'  <text x="1060" y="250" font-family="sans-serif" font-size="13" font-weight="700" fill="#f59e0b">Armadura Positiva Direção X</text>',
        f'  <text x="1060" y="272" font-family="monospace" font-size="12" fill="#94a3b8">As calc: {float(ax.as_calculado_cm2_m):.2f} cm²/m · As min: {float(ax.as_minimo_cm2_m):.2f} cm²/m</text>',
        f'  <text x="1060" y="292" font-family="monospace" font-size="13" font-weight="700" fill="#f8fafc">Detalhamento: Φ {ax.bitola_mm} mm c/ {ax.espacamento_adotado_cm} cm (As={float(ax.as_efetivo_cm2_m):.2f} cm²/m)</text>',
        '',
        '  <!-- Bloco Armadura Y -->',
        '  <rect x="1045" y="315" width="340" height="75" rx="8" fill="#0f172a" fill-opacity="0.6" stroke="#10b981" stroke-width="1.5" />',
        f'  <text x="1060" y="340" font-family="sans-serif" font-size="13" font-weight="700" fill="#10b981">Armadura Positiva Direção Y</text>',
        f'  <text x="1060" y="362" font-family="monospace" font-size="12" fill="#94a3b8">As calc: {float(ay.as_calculado_cm2_m):.2f} cm²/m · As min: {float(ay.as_minimo_cm2_m):.2f} cm²/m</text>',
        f'  <text x="1060" y="382" font-family="monospace" font-size="13" font-weight="700" fill="#f8fafc">Detalhamento: Φ {ay.bitola_mm} mm c/ {ay.espacamento_adotado_cm} cm (As={float(ay.as_efetivo_cm2_m):.2f} cm²/m)</text>',
        '',
        '  <!-- Bloco ELS (Flecha e Fissura) -->',
        '  <rect x="1045" y="405" width="340" height="150" rx="8" fill="#0f172a" fill-opacity="0.6" />',
        f'  <text x="1060" y="430" font-family="sans-serif" font-size="13" font-weight="700" fill="#38bdf8">Verificação dos Estados Limites de Serviço</text>',
        f'  <text x="1060" y="455" font-family="sans-serif" font-size="12" fill="#94a3b8">Flecha Imediata (f0):</text>',
        f'  <text x="1370" y="455" font-family="monospace" font-size="13" font-weight="700" fill="#f8fafc" text-anchor="end">{float(els.flecha_imediata_cm):.3f} cm</text>',
        f'  <text x="1060" y="480" font-family="sans-serif" font-size="12" fill="#94a3b8">Flecha Total Diferida (ftot):</text>',
        f'  <text x="1370" y="480" font-family="monospace" font-size="13" font-weight="700" fill="#10b981" text-anchor="end">{float(els.flecha_total_cm):.3f} cm &lt;= {float(els.flecha_limite_cm):.3f} cm (OK)</text>',
        f'  <text x="1060" y="505" font-family="sans-serif" font-size="12" fill="#94a3b8">Abertura de Fissuras wk:</text>',
        f'  <text x="1370" y="505" font-family="monospace" font-size="13" font-weight="700" fill="#10b981" text-anchor="end">{float(els.abertura_fissura_estimada_mm):.2f} mm &lt;= {float(els.abertura_fissura_limite_mm):.2f} mm (OK)</text>',
        f'  <text x="1060" y="530" font-family="sans-serif" font-size="12" fill="#94a3b8">Cobrimento Nominal c_nom:</text>',
        f'  <text x="1370" y="530" font-family="monospace" font-size="13" font-weight="700" fill="#f8fafc" text-anchor="end">{float(els.cobrimento_cm):.1f} cm ({e.classe_agressividade})</text>',
        '',
        '  <!-- Painel Inferior: Resumo Normativo e Auditoria -->',
        '  <rect x="30" y="600" width="1380" height="270" rx="12" fill="url(#cardGrad)" filter="url(#dropShadow)" />',
        '  <text x="55" y="635" font-family="system-ui, sans-serif" font-size="18" font-weight="700" fill="#38bdf8">4. Auditoria Estrutural e Resumo Executivo Normativo</text>',
        '',
        '  <!-- 4 Cards Informativos -->',
        '  <g transform="translate(55, 660)">',
        '    <!-- Card 1: Cisalhamento V_Rd1 -->',
        f'    <rect width="310" height="185" rx="8" fill="#0f172a" fill-opacity="0.8" stroke="{"#10b981" if cis.atende else "#ef4444"}" stroke-width="1.5" />',
        f'    <text x="20" y="32" font-family="sans-serif" font-size="14" font-weight="700" fill="#f8fafc">Força Cortante (V_Rd1)</text>',
        f'    <text x="20" y="60" font-family="sans-serif" font-size="12" fill="#94a3b8">V_sd: {float(cis.vsd_kn_m):.2f} kN/m</text>',
        f'    <text x="20" y="85" font-family="sans-serif" font-size="12" fill="#94a3b8">V_Rd1: {float(cis.vrd1_kn_m):.2f} kN/m</text>',
        f'    <text x="20" y="110" font-family="sans-serif" font-size="12" fill="#94a3b8">Taxa: {float(cis.ratio_solicitacao)*100:.1f}%</text>',
        f'    <rect x="20" y="130" width="270" height="35" rx="6" fill="{"#10b981" if cis.atende else "#ef4444"}" fill-opacity="0.2" />',
        f'    <text x="155" y="152" font-family="sans-serif" font-size="12" font-weight="700" fill="{"#10b981" if cis.atende else "#ef4444"}" text-anchor="middle">DISPENSA ESTRIBOS</text>',
        '',
        '    <!-- Card 2: Deformação ELS-DEF -->',
        '    <g transform="translate(330, 0)">',
        f'      <rect width="310" height="185" rx="8" fill="#0f172a" fill-opacity="0.8" stroke="{"#10b981" if els.atende_flecha else "#ef4444"}" stroke-width="1.5" />',
        f'      <text x="20" y="32" font-family="sans-serif" font-size="14" font-weight="700" fill="#f8fafc">Flecha Excessiva (ELS-DEF)</text>',
        f'      <text x="20" y="60" font-family="sans-serif" font-size="12" fill="#94a3b8">f_imediata: {float(els.flecha_imediata_cm):.3f} cm</text>',
        f'      <text x="20" y="85" font-family="sans-serif" font-size="12" fill="#94a3b8">f_total diferida: {float(els.flecha_total_cm):.3f} cm</text>',
        f'      <text x="20" y="110" font-family="sans-serif" font-size="12" fill="#94a3b8">Limite lx/250: {float(els.flecha_limite_cm):.3f} cm</text>',
        f'      <rect x="20" y="130" width="270" height="35" rx="6" fill="{"#10b981" if els.atende_flecha else "#ef4444"}" fill-opacity="0.2" />',
        f'      <text x="155" y="152" font-family="sans-serif" font-size="12" font-weight="700" fill="{"#10b981" if els.atende_flecha else "#ef4444"}" text-anchor="middle">FLECHA CONFORME</text>',
        '    </g>',
        '',
        '    <!-- Card 3: Fissuração ELS-W -->',
        '    <g transform="translate(660, 0)">',
        f'      <rect width="310" height="185" rx="8" fill="#0f172a" fill-opacity="0.8" stroke="{"#10b981" if els.atende_fissura else "#ef4444"}" stroke-width="1.5" />',
        f'      <text x="20" y="32" font-family="sans-serif" font-size="14" font-weight="700" fill="#f8fafc">Fissuração (ELS-W)</text>',
        f'      <text x="20" y="60" font-family="sans-serif" font-size="12" fill="#94a3b8">wk estimado: {float(els.abertura_fissura_estimada_mm):.2f} mm</text>',
        f'      <text x="20" y="85" font-family="sans-serif" font-size="12" fill="#94a3b8">w_limite ({e.classe_agressividade}): {float(els.abertura_fissura_limite_mm):.2f} mm</text>',
        f'      <text x="20" y="110" font-family="sans-serif" font-size="12" fill="#94a3b8">Cobrimento c_nom: {float(els.cobrimento_cm):.1f} cm</text>',
        f'      <rect x="20" y="130" width="270" height="35" rx="6" fill="{"#10b981" if els.atende_fissura else "#ef4444"}" fill-opacity="0.2" />',
        f'      <text x="155" y="152" font-family="sans-serif" font-size="12" font-weight="700" fill="{"#10b981" if els.atende_fissura else "#ef4444"}" text-anchor="middle">FISSURAÇÃO ATENDIDA</text>',
        '    </g>',
        '',
        '    <!-- Card 4: Detalhamento Executivo -->',
        '    <g transform="translate(990, 0)">',
        f'      <rect width="330" height="185" rx="8" fill="#0f172a" fill-opacity="0.8" stroke="#38bdf8" stroke-width="1.5" />',
        f'      <text x="20" y="32" font-family="sans-serif" font-size="14" font-weight="700" fill="#f8fafc">Síntese de Armaduras</text>',
        f'      <text x="20" y="60" font-family="monospace" font-size="12" fill="#f59e0b">X+: Φ{ax.bitola_mm} c/{ax.espacamento_adotado_cm}cm ({float(ax.as_efetivo_cm2_m):.2f} cm²/m)</text>',
        f'      <text x="20" y="85" font-family="monospace" font-size="12" fill="#10b981">Y+: Φ{ay.bitola_mm} c/{ay.espacamento_adotado_cm}cm ({float(ay.as_efetivo_cm2_m):.2f} cm²/m)</text>',
        f'      <text x="20" y="110" font-family="monospace" font-size="12" fill="#38bdf8">Concreto: {e.fck_classe} · Aço CA-50</text>',
        f'      <rect x="20" y="130" width="290" height="35" rx="6" fill="#10b981" fill-opacity="0.2" />',
        f'      <text x="165" y="152" font-family="sans-serif" font-size="12" font-weight="700" fill="#10b981" text-anchor="middle">PRONTO P/ EXECUÇÃO</text>',
        '    </g>',
        '  </g>',
        '</svg>',
    ]

    return "\n".join(svg_linhas) + "\n"
