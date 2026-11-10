"""Modelos de dados imutáveis para dimensionamento de lajes maciças (ABNT NBR 6118:2023).

Garante total tipagem estática e imutabilidade estrutural com frações exatas.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Literal

TipoVinculacao = Literal["APOIADA", "ENGASTADA", "LIVRE"]
TipoArmacao = Literal["CRUZ", "UNIDIRECIONAL"]


@dataclass(frozen=True)
class VinculacoesBordas:
    """Condições de contorno nas 4 bordas da laje retangular.
    
    x0, x1: bordas paralelas ao eixo Y (ao longo do vão lx).
    y0, y1: bordas paralelas ao eixo X (ao longo do vão ly).
    """
    borda_x0: TipoVinculacao
    borda_x1: TipoVinculacao
    borda_y0: TipoVinculacao
    borda_y1: TipoVinculacao

    def total_engastes(self) -> int:
        return sum(1 for b in (self.borda_x0, self.borda_x1, self.borda_y0, self.borda_y1) if b == "ENGASTADA")

    def total_apoios(self) -> int:
        return sum(1 for b in (self.borda_x0, self.borda_x1, self.borda_y0, self.borda_y1) if b == "APOIADA")

    def total_livres(self) -> int:
        return sum(1 for b in (self.borda_x0, self.borda_x1, self.borda_y0, self.borda_y1) if b == "LIVRE")


@dataclass(frozen=True)
class LajeEntrada:
    """Parâmetros geométricos, mecânicos e de carregamento de entrada para a laje."""
    identificador: str
    lx_m: Fraction                      # Menor vão livre/efetivo em metros
    ly_m: Fraction                      # Maior vão livre/efetivo em metros (ly >= lx)
    h_cm: Fraction                      # Espessura total da laje em cm
    fck_classe: str                     # Ex: "C25", "C30"
    classe_agressividade: str           # Ex: "CAA_I", "CAA_II"
    tipo_uso: str                       # Ex: "PISO_NAO_BALANCO", "COBERTURA_NAO_BALANCO"
    g_adicional_kn_m2: Fraction         # Revestimento, forro, contrapiso (kN/m²)
    q_acidental_kn_m2: Fraction         # Sobrecarga de uso normativo (kN/m²)
    vinculacoes: VinculacoesBordas
    bitola_x_mm: str = "8.0"            # Bitola principal adotada na direção X
    bitola_y_mm: str = "8.0"            # Bitola na direção Y
    bitola_engaste_mm: str = "10.0"     # Bitola para momentos negativos de engaste


@dataclass(frozen=True)
class CarregamentosLaje:
    """Cargas permanentes, acidentais e de cálculo na laje em kN/m²."""
    g_peso_proprio_kn_m2: Fraction
    g_total_kn_m2: Fraction
    q_servico_kn_m2: Fraction
    p_servico_kn_m2: Fraction
    p_calculo_kn_m2: Fraction           # p_d = 1.4 * p_servico


@dataclass(frozen=True)
class EsforcosLaje:
    """Esforços solicitantes característicos e de cálculo (kN.m/m e kN/m)."""
    lambda_relacao: Fraction            # ly / lx
    tipo_armacao: TipoArmacao           # "CRUZ" (lambda <= 2) ou "UNIDIRECIONAL" (lambda > 2)
    tipo_marcus: str                    # Ex: "TIPO_1", "TIPO_2A", etc.
    mx_k_kn_m_m: Fraction               # Momento fletor positivo em X característico
    my_k_kn_m_m: Fraction               # Momento fletor positivo em Y característico
    mxe_k_kn_m_m: Fraction              # Momento negativo em X (engaste) característico
    mye_k_kn_m_m: Fraction              # Momento negativo em Y (engaste) característico
    mxd_kn_m_m: Fraction                # Momento positivo em X de cálculo (ELU)
    myd_kn_m_m: Fraction                # Momento positivo em Y de cálculo (ELU)
    mxed_kn_m_m: Fraction               # Momento negativo em X de cálculo (ELU)
    myed_kn_m_m: Fraction               # Momento negativo em Y de cálculo (ELU)
    vx_kn_m: Fraction                   # Reação de apoio linear distribuída em X (kN/m)
    vy_kn_m: Fraction                   # Reação de apoio linear distribuída em Y (kN/m)


@dataclass(frozen=True)
class ArmaduraFaixa:
    """Detalhamento da armadura em uma faixa de 1 metro de largura."""
    direcao: str                        # "X_POSITIVA", "Y_POSITIVA", "X_NEGATIVA", "Y_NEGATIVA", "DISTRIBUICAO_SECUNDARIA"
    momento_calculo_kn_m_m: Fraction
    d_util_cm: Fraction
    as_calculado_cm2_m: Fraction
    as_minimo_cm2_m: Fraction
    as_adotado_cm2_m: Fraction
    bitola_mm: str
    espacamento_calculado_cm: Fraction
    espacamento_adotado_cm: int
    numero_barras_por_metro: int
    as_efetivo_cm2_m: Fraction


@dataclass(frozen=True)
class VerificacaoCisalhamento:
    """Verificação da força cortante resistente sem armadura transversal (V_Rd1)."""
    vsd_kn_m: Fraction                  # Força cortante solicitante máxima de cálculo
    vrd1_kn_m: Fraction                 # Força cortante resistente da laje sem armadura
    ratio_solicitacao: Fraction         # vsd / vrd1
    atende: bool
    mensagem: str


@dataclass(frozen=True)
class VerificacaoELS:
    """Verificação dos Estados Limites de Serviço (Deformação e Fissuração)."""
    cobrimento_cm: Fraction
    flecha_imediata_cm: Fraction
    flecha_diferida_cm: Fraction
    flecha_total_cm: Fraction
    flecha_limite_cm: Fraction          # lx / 250
    atende_flecha: bool
    abertura_fissura_estimada_mm: Fraction
    abertura_fissura_limite_mm: Fraction
    atende_fissura: bool


@dataclass(frozen=True)
class ResultadoLaje:
    """Consolidação completa do dimensionamento, detalhamento e verificações normativas."""
    entrada: LajeEntrada
    carregamentos: CarregamentosLaje
    esforcos: EsforcosLaje
    armaduras: dict[str, ArmaduraFaixa]
    cisalhamento: VerificacaoCisalhamento
    els: VerificacaoELS
    conformidade_geral: bool
    resumo_executivo: str
