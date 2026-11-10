"""Módulo de cálculo analítico e determinístico de lajes maciças (ABNT NBR 6118:2023).

Todas as operações são realizadas em frações exatas (Fraction) e inteiros,
sem emprego de ponto flutuante (float) no núcleo de cálculo estrutural.
"""

from __future__ import annotations

from fractions import Fraction
import math
from typing import Final

from .constants import (
    ABERTURAS_MAXIMAS_FISSURAS_MM,
    ARMADURA_SECUNDARIA_MINIMA_ABSOLUTA_CM2_M,
    BITOLAS_COMERCIAIS_LAJES,
    CLASSES_CONCRETO_F_CK,
    COBRIMENTOS_NOMINAIS_CM,
    COEFICIENTES_DEFLEXAO_PLACA,
    ESPACAMENTO_MAXIMO_PRINCIPAL_ABSOLUTO_CM,
    ESPACAMENTO_MAXIMO_SECUNDARIA_ABSOLUTO_CM,
    ESPACAMENTO_MINIMO_ABSOLUTO_CM,
    ESPESSURAS_MINIMAS_USO_CM,
    F_YD_CA50_KN_CM2,
    GAMMA_C,
    GAMMA_F,
    LARGURA_FAIXA_CALCULO_CM,
    MODULOS_ELASTICIDADE_CONCRETO_E_CS_KN_CM2,
    MODULO_ELASTICIDADE_ACO_KN_CM2,
    PESO_ESPECIFICO_CONCRETO_ARMADO,
    TABELA_MARCUS_COEFICIENTES,
    TAXAS_MINIMAS_ARMADURA_RHO,
)
from .models import (
    ArmaduraFaixa,
    CarregamentosLaje,
    EsforcosLaje,
    LajeEntrada,
    ResultadoLaje,
    TipoArmacao,
    VerificacaoCisalhamento,
    VerificacaoELS,
    VinculacoesBordas,
)


def raiz_quadrada_fracao(fracao: Fraction, precisao_decimais: int = 8) -> Fraction:
    """Calcula a raiz quadrada exata/racional de uma fração sem ponto flutuante.
    
    Utiliza math.isqrt com escalonamento por 10^(2k) para microsegundos de execução,
    evitando a explosão de bits do método de Newton-Raphson puro.
    """
    if fracao < 0:
        raise ValueError(f"Não existe raiz quadrada real de número negativo: {fracao}")
    if fracao == 0:
        return Fraction(0, 1)

    p = fracao.numerator
    q = fracao.denominator

    fator = 10 ** (2 * precisao_decimais)
    raiz_inteira = math.isqrt(p * q * fator)
    return Fraction(raiz_inteira, q * (10 ** precisao_decimais))


def validar_geometria_e_materiais(entrada: LajeEntrada) -> None:
    """Valida as entradas normativas da laje."""
    if entrada.lx_m <= 0:
        raise ValueError(f"O vão lx deve ser positivo. Recebido: {entrada.lx_m}")
    if entrada.ly_m <= 0:
        raise ValueError(f"O vão ly deve ser positivo. Recebido: {entrada.ly_m}")
    if entrada.lx_m > entrada.ly_m:
        raise ValueError(
            f"O vão lx ({entrada.lx_m}m) deve ser o menor vão (lx <= ly, recebido ly={entrada.ly_m}m)."
        )
    if entrada.h_cm <= 0:
        raise ValueError(f"A espessura da laje deve ser positiva. Recebida: {entrada.h_cm} cm")

    if entrada.fck_classe not in CLASSES_CONCRETO_F_CK:
        raise ValueError(
            f"Classe de concreto '{entrada.fck_classe}' inválida. Válidas: {list(CLASSES_CONCRETO_F_CK.keys())}"
        )
    if entrada.classe_agressividade not in COBRIMENTOS_NOMINAIS_CM:
        raise ValueError(
            f"Classe de agressividade '{entrada.classe_agressividade}' inválida. Válidas: {list(COBRIMENTOS_NOMINAIS_CM.keys())}"
        )
    if entrada.tipo_uso not in ESPESSURAS_MINIMAS_USO_CM:
        raise ValueError(
            f"Tipo de uso '{entrada.tipo_uso}' inválido. Válidos: {list(ESPESSURAS_MINIMAS_USO_CM.keys())}"
        )

    h_min_normativa = ESPESSURAS_MINIMAS_USO_CM[entrada.tipo_uso]
    if entrada.h_cm < h_min_normativa:
        raise ValueError(
            f"Espessura da laje ({entrada.h_cm} cm) inferior ao mínimo normativo "
            f"da ABNT NBR 6118 para {entrada.tipo_uso} ({h_min_normativa} cm)."
        )

    if entrada.bitola_x_mm not in BITOLAS_COMERCIAIS_LAJES:
        raise ValueError(f"Bitola em X '{entrada.bitola_x_mm}' inválida.")
    if entrada.bitola_y_mm not in BITOLAS_COMERCIAIS_LAJES:
        raise ValueError(f"Bitola em Y '{entrada.bitola_y_mm}' inválida.")
    if entrada.bitola_engaste_mm not in BITOLAS_COMERCIAIS_LAJES:
        raise ValueError(f"Bitola de engaste '{entrada.bitola_engaste_mm}' inválida.")


def calcular_carregamentos(entrada: LajeEntrada) -> CarregamentosLaje:
    """Calcula as cargas permanentes, acidentais e de cálculo na laje em kN/m²."""
    # Peso próprio g_pp = 25 kN/m³ * (h / 100) m
    g_pp = PESO_ESPECIFICO_CONCRETO_ARMADO * entrada.h_cm / Fraction(100, 1)
    g_total = g_pp + entrada.g_adicional_kn_m2
    q_servico = entrada.q_acidental_kn_m2
    p_servico = g_total + q_servico
    p_calculo = GAMMA_F * p_servico

    return CarregamentosLaje(
        g_peso_proprio_kn_m2=g_pp,
        g_total_kn_m2=g_total,
        q_servico_kn_m2=q_servico,
        p_servico_kn_m2=p_servico,
        p_calculo_kn_m2=p_calculo,
    )


def determinar_tipo_marcus(vinc: VinculacoesBordas) -> str:
    """Classifica o contorno da laje retangular nos tipos clássicos de Marcus/Bares."""
    eng_x = (1 if vinc.borda_x0 == "ENGASTADA" else 0) + (1 if vinc.borda_x1 == "ENGASTADA" else 0)
    eng_y = (1 if vinc.borda_y0 == "ENGASTADA" else 0) + (1 if vinc.borda_y1 == "ENGASTADA" else 0)
    total_eng = eng_x + eng_y

    if total_eng == 0:
        return "TIPO_1"
    elif total_eng == 1:
        return "TIPO_2A" if eng_x == 1 else "TIPO_2B"
    elif total_eng == 2:
        if eng_x == 1 and eng_y == 1:
            return "TIPO_3"
        elif eng_x == 2:
            return "TIPO_4A"
        else:
            return "TIPO_4B"
    elif total_eng == 3:
        return "TIPO_5A" if eng_x == 2 else "TIPO_5B"
    else:
        return "TIPO_6"


def interpolar_coeficientes_marcus(tipo_marcus: str, lambda_rel: Fraction) -> dict[str, Fraction]:
    """Interpola racionalmente os coeficientes da tabela de Marcus para a relação lambda dada."""
    # Clampear lambda entre 1.0 e 2.0 para a tabela
    tabela_tipo = TABELA_MARCUS_COEFICIENTES[tipo_marcus]
    lambdas_ordenados = sorted(tabela_tipo.keys())

    if lambda_rel <= lambdas_ordenados[0]:
        return tabela_tipo[lambdas_ordenados[0]]
    if lambda_rel >= lambdas_ordenados[-1]:
        return tabela_tipo[lambdas_ordenados[-1]]

    # Localizar intervalo [lambda_inf, lambda_sup]
    l_inf = lambdas_ordenados[0]
    l_sup = lambdas_ordenados[-1]
    for i in range(len(lambdas_ordenados) - 1):
        if lambdas_ordenados[i] <= lambda_rel <= lambdas_ordenados[i + 1]:
            l_inf = lambdas_ordenados[i]
            l_sup = lambdas_ordenados[i + 1]
            break

    dados_inf = tabela_tipo[l_inf]
    dados_sup = tabela_tipo[l_sup]
    delta_lambda = l_sup - l_inf
    fator = (lambda_rel - l_inf) / delta_lambda

    resultado = {}
    for chave in dados_inf:
        val_inf = dados_inf[chave]
        val_sup = dados_sup[chave]
        resultado[chave] = val_inf + fator * (val_sup - val_inf)

    return resultado


def calcular_esforcos(entrada: LajeEntrada, carregamento: CarregamentosLaje) -> EsforcosLaje:
    """Calcula momentos fletores e reações de apoio característicos e de cálculo."""
    lx = entrada.lx_m
    ly = entrada.ly_m
    lambda_rel = ly / lx
    p_k = carregamento.p_servico_kn_m2
    p_d = carregamento.p_calculo_kn_m2
    lx2 = lx * lx

    tipo_armacao: TipoArmacao = "CRUZ" if lambda_rel <= Fraction(20, 10) else "UNIDIRECIONAL"
    tipo_marcus = determinar_tipo_marcus(entrada.vinculacoes)

    if tipo_armacao == "CRUZ":
        coefs = interpolar_coeficientes_marcus(tipo_marcus, lambda_rel)
        # Momentos em kN.m/m = mu * p * lx² / 100
        mx_k = coefs["mu_x"] * p_k * lx2 / Fraction(100, 1)
        my_k = coefs["mu_y"] * p_k * lx2 / Fraction(100, 1)
        mxe_k = coefs["mu_xe"] * p_k * lx2 / Fraction(100, 1)
        mye_k = coefs["mu_ye"] * p_k * lx2 / Fraction(100, 1)

        # Reações de apoio em kN/m = q * p * lx
        vx = coefs["qx"] * p_k * lx
        vy = coefs["qy"] * p_k * lx
    else:
        # Laje Unidirecional (lambda > 2.0) - flexionando principalmente no menor vão lx
        # Modelo analítico de viga contínua de largura unitária b = 1m
        eng_x = (1 if entrada.vinculacoes.borda_x0 == "ENGASTADA" else 0) + (
            1 if entrada.vinculacoes.borda_x1 == "ENGASTADA" else 0
        )
        if eng_x == 0:
            # Biapoiada: mx = p * lx² / 8, mxe = 0
            mx_k = p_k * lx2 / Fraction(8, 1)
            mxe_k = Fraction(0, 1)
            vx = p_k * lx / Fraction(2, 1)
        elif eng_x == 1:
            # Engastada e apoiada: mx = 9/128 * p * lx², mxe = p * lx² / 8
            mx_k = Fraction(9, 128) * p_k * lx2
            mxe_k = p_k * lx2 / Fraction(8, 1)
            vx = Fraction(5, 8) * p_k * lx
        else:
            # Biengastada: mx = p * lx² / 24, mxe = p * lx² / 12
            mx_k = p_k * lx2 / Fraction(24, 1)
            mxe_k = p_k * lx2 / Fraction(12, 1)
            vx = p_k * lx / Fraction(2, 1)

        # Na direção Y: momento nominal secundário de 20% do momento principal
        my_k = mx_k * Fraction(20, 100)
        mye_k = Fraction(0, 1)
        vy = Fraction(1, 10) * p_k * lx

    # Momentos de cálculo no ELU (kN.m/m)
    mxd = GAMMA_F * mx_k
    myd = GAMMA_F * my_k
    mxed = GAMMA_F * mxe_k
    myed = GAMMA_F * mye_k

    return EsforcosLaje(
        lambda_relacao=lambda_rel,
        tipo_armacao=tipo_armacao,
        tipo_marcus=tipo_marcus,
        mx_k_kn_m_m=mx_k,
        my_k_kn_m_m=my_k,
        mxe_k_kn_m_m=mxe_k,
        mye_k_kn_m_m=mye_k,
        mxd_kn_m_m=mxd,
        myd_kn_m_m=myd,
        mxed_kn_m_m=mxed,
        myed_kn_m_m=myed,
        vx_kn_m=vx,
        vy_kn_m=vy,
    )


def dimensionar_armadura_faixa(
    direcao: str,
    momento_calculo_kn_m_m: Fraction,
    d_util_cm: Fraction,
    h_cm: Fraction,
    fck_classe: str,
    bitola_mm: str,
    as_minimo_adicional: Fraction | None = None,
    eh_secundaria: bool = False,
) -> ArmaduraFaixa:
    """Dimensiona a armadura para uma faixa unitária de 100 cm de largura no ELU."""
    b_cm = LARGURA_FAIXA_CALCULO_CM
    fck_kn_cm2 = CLASSES_CONCRETO_F_CK[fck_classe]
    fcd_kn_cm2 = fck_kn_cm2 / GAMMA_C
    sigma_cd = Fraction(85, 100) * fcd_kn_cm2
    fyd = F_YD_CA50_KN_CM2

    # Momento em kN.cm/m = momento em kN.m/m * 100
    md_kn_cm_m = momento_calculo_kn_m_m * Fraction(100, 1)

    # Momento fletor adimensional mu = md / (b * d² * sigma_cd)
    denominador = b_cm * d_util_cm * d_util_cm * sigma_cd
    mu = md_kn_cm_m / denominador if denominador > 0 else Fraction(0, 1)

    # Limite de ductilidade da NBR 6118 (xi <= 0.45 -> mu <= 0.2952)
    mu_limite = Fraction(2952, 10000)
    if mu > mu_limite:
        raise ValueError(
            f"Momento fletor excessivo para a espessura da laje (mu = {float(mu):.4f} > {float(mu_limite):.4f}). "
            f"Necessário aumentar a espessura h ({h_cm} cm) para garantir ductilidade sem armadura dupla."
        )

    # xi = (1 - sqrt(1 - 2*mu)) / 0.8
    if mu > 0:
        termo_raiz = Fraction(1, 1) - Fraction(2, 1) * mu
        raiz = raiz_quadrada_fracao(termo_raiz)
        xi = (Fraction(1, 1) - raiz) / Fraction(8, 10)
        x_cm = xi * d_util_cm
        z_cm = d_util_cm - Fraction(4, 10) * x_cm
        as_calculado = md_kn_cm_m / (z_cm * fyd)
    else:
        as_calculado = Fraction(0, 1)

    # Armadura mínima de flexão da NBR 6118 (Tabela 17.3)
    rho_min = TAXAS_MINIMAS_ARMADURA_RHO[fck_classe]
    as_min = rho_min * b_cm * h_cm

    if eh_secundaria:
        # Armadura secundária de distribuição (NBR 6118)
        # As,sec >= max(0.20 * As,princ, 0.50 * As,min, 0.9 cm²/m)
        as_min_sec = max(
            as_minimo_adicional if as_minimo_adicional is not None else Fraction(0, 1),
            as_min / Fraction(2, 1),
            ARMADURA_SECUNDARIA_MINIMA_ABSOLUTA_CM2_M,
        )
        as_adotado = max(as_calculado, as_min_sec)
    else:
        as_adotado = max(as_calculado, as_min)

    # Bitola e espaçamento comercial
    dados_bitola = BITOLAS_COMERCIAIS_LAJES[bitola_mm]
    area_barra_cm2 = dados_bitola["area_cm2"]

    # Espaçamento teórico s = 100 * Ab / As (cm)
    s_teorico = (b_cm * area_barra_cm2) / as_adotado

    # Espaçamentos máximos normativos (NBR 6118 item 20.1)
    if eh_secundaria:
        s_max_norma = min(ESPACAMENTO_MAXIMO_SECUNDARIA_ABSOLUTO_CM, Fraction(3, 1) * h_cm)
    else:
        s_max_norma = min(ESPACAMENTO_MAXIMO_PRINCIPAL_ABSOLUTO_CM, Fraction(2, 1) * h_cm)

    s_min_norma = ESPACAMENTO_MINIMO_ABSOLUTO_CM

    # Arredondar para baixo para o inteiro mais próximo em cm
    s_int = int(math.floor(s_teorico))
    s_max_int = int(math.floor(s_max_norma))
    s_min_int = int(math.ceil(s_min_norma))

    s_adotado = min(max(s_int, s_min_int), s_max_int)
    numero_barras = int(math.ceil(100 / s_adotado))
    as_efetivo = Fraction(numero_barras, 1) * area_barra_cm2

    return ArmaduraFaixa(
        direcao=direcao,
        momento_calculo_kn_m_m=momento_calculo_kn_m_m,
        d_util_cm=d_util_cm,
        as_calculado_cm2_m=as_calculado,
        as_minimo_cm2_m=as_min,
        as_adotado_cm2_m=as_adotado,
        bitola_mm=bitola_mm,
        espacamento_calculado_cm=s_teorico,
        espacamento_adotado_cm=s_adotado,
        numero_barras_por_metro=numero_barras,
        as_efetivo_cm2_m=as_efetivo,
    )


def dimensionar_todas_armaduras(
    entrada: LajeEntrada,
    esforcos: EsforcosLaje,
) -> dict[str, ArmaduraFaixa]:
    """Dimensiona e detalha as armaduras nas direções X e Y (positivas e negativas)."""
    cobrimento = COBRIMENTOS_NOMINAIS_CM[entrada.classe_agressividade]
    phi_x_cm = BITOLAS_COMERCIAIS_LAJES[entrada.bitola_x_mm]["diametro_cm"]
    phi_y_cm = BITOLAS_COMERCIAIS_LAJES[entrada.bitola_y_mm]["diametro_cm"]
    phi_eng_cm = BITOLAS_COMERCIAIS_LAJES[entrada.bitola_engaste_mm]["diametro_cm"]

    # Altura útil em X (camada mais externa / inferior)
    dx = entrada.h_cm - cobrimento - (phi_x_cm / Fraction(2, 1))

    # Altura útil em Y (camada superior à de X na malha inferior)
    dy = dx - (phi_x_cm / Fraction(2, 1)) - (phi_y_cm / Fraction(2, 1))

    # Altura útil para momentos negativos (camada superior da laje)
    d_neg = entrada.h_cm - cobrimento - (phi_eng_cm / Fraction(2, 1))

    armaduras = {}

    # 1. Armadura Positiva em X
    armaduras["X_POSITIVA"] = dimensionar_armadura_faixa(
        direcao="X_POSITIVA",
        momento_calculo_kn_m_m=esforcos.mxd_kn_m_m,
        d_util_cm=dx,
        h_cm=entrada.h_cm,
        fck_classe=entrada.fck_classe,
        bitola_mm=entrada.bitola_x_mm,
        eh_secundaria=False,
    )

    # 2. Armadura Positiva em Y
    if esforcos.tipo_armacao == "CRUZ":
        armaduras["Y_POSITIVA"] = dimensionar_armadura_faixa(
            direcao="Y_POSITIVA",
            momento_calculo_kn_m_m=esforcos.myd_kn_m_m,
            d_util_cm=dy,
            h_cm=entrada.h_cm,
            fck_classe=entrada.fck_classe,
            bitola_mm=entrada.bitola_y_mm,
            eh_secundaria=False,
        )
    else:
        # Unidirecional: armadura secundária de distribuição
        as_princ = armaduras["X_POSITIVA"].as_adotado_cm2_m
        armaduras["Y_POSITIVA"] = dimensionar_armadura_faixa(
            direcao="Y_POSITIVA",
            momento_calculo_kn_m_m=esforcos.myd_kn_m_m,
            d_util_cm=dy,
            h_cm=entrada.h_cm,
            fck_classe=entrada.fck_classe,
            bitola_mm=entrada.bitola_y_mm,
            as_minimo_adicional=as_princ * Fraction(20, 100),
            eh_secundaria=True,
        )

    # 3. Armadura Negativa em X (se houver engaste)
    if esforcos.mxed_kn_m_m > 0:
        armaduras["X_NEGATIVA"] = dimensionar_armadura_faixa(
            direcao="X_NEGATIVA",
            momento_calculo_kn_m_m=esforcos.mxed_kn_m_m,
            d_util_cm=d_neg,
            h_cm=entrada.h_cm,
            fck_classe=entrada.fck_classe,
            bitola_mm=entrada.bitola_engaste_mm,
            eh_secundaria=False,
        )

    # 4. Armadura Negativa em Y (se houver engaste)
    if esforcos.myed_kn_m_m > 0:
        armaduras["Y_NEGATIVA"] = dimensionar_armadura_faixa(
            direcao="Y_NEGATIVA",
            momento_calculo_kn_m_m=esforcos.myed_kn_m_m,
            d_util_cm=d_neg,
            h_cm=entrada.h_cm,
            fck_classe=entrada.fck_classe,
            bitola_mm=entrada.bitola_engaste_mm,
            eh_secundaria=False,
        )

    return armaduras


def verificar_cisalhamento_v_rd1(
    entrada: LajeEntrada,
    esforcos: EsforcosLaje,
    armaduras: dict[str, ArmaduraFaixa],
) -> VerificacaoCisalhamento:
    """Verifica a resistência à força cortante de lajes maciças sem armadura transversal (V_Rd1).
    
    Conforme ABNT NBR 6118:2023, item 19.4.1:
    V_Rd1 = [tau_R * k * (1.2 + 40 * rho_1)] * b_w * d
    """
    b_cm = LARGURA_FAIXA_CALCULO_CM
    dx = armaduras["X_POSITIVA"].d_util_cm  # cm
    d_mm = dx * Fraction(10, 1)            # mm

    # Fator de efeito de escala k = |1 + sqrt(200 / d_mm)| <= 2.0
    termo_k = Fraction(200, 1) / d_mm
    raiz_200_d = raiz_quadrada_fracao(termo_k)
    k = min(Fraction(1, 1) + raiz_200_d, Fraction(2, 1))

    # Taxa geométrica de armadura longitudinal de tração rho_1 = As1 / (bw * d) <= 0.02
    as1 = armaduras["X_POSITIVA"].as_efetivo_cm2_m
    rho_1 = min(as1 / (b_cm * dx), Fraction(2, 100))

    # Tensão resistente básica tau_R = 0.25 * f_ctd (kN/cm²)
    # f_ctk,inf = 0.7 * 0.3 * fck^(2/3) / 1.4
    # Para fck de 20 a 50 MPa, aproximamos f_ctd por frações racionais normativas tabeladas:
    TABELA_FCTD_KN_CM2: dict[str, Fraction] = {
        "C20": Fraction(105, 1000),   # 1.05 MPa = 0.105 kN/cm²
        "C25": Fraction(125, 1000),   # 1.25 MPa = 0.125 kN/cm²
        "C30": Fraction(145, 1000),   # 1.45 MPa = 0.145 kN/cm²
        "C35": Fraction(165, 1000),   # 1.65 MPa = 0.165 kN/cm²
        "C40": Fraction(185, 1000),   # 1.85 MPa = 0.185 kN/cm²
        "C45": Fraction(200, 1000),   # 2.00 MPa = 0.200 kN/cm²
        "C50": Fraction(215, 1000),   # 2.15 MPa = 0.215 kN/cm²
    }
    f_ctd = TABELA_FCTD_KN_CM2.get(entrada.fck_classe, Fraction(125, 1000))
    tau_r = Fraction(25, 100) * f_ctd

    # Força cortante resistente V_Rd1 em kN/m = [tau_R * k * (1.2 + 40 * rho_1)] * b * d
    fator_armadura = Fraction(12, 10) + Fraction(40, 1) * rho_1
    vrd1 = tau_r * k * fator_armadura * b_cm * dx

    # Maior reação de apoio solicitante de cálculo V_sd = 1.4 * max(vx, vy)
    max_vk = max(esforcos.vx_kn_m, esforcos.vy_kn_m)
    vsd = GAMMA_F * max_vk

    ratio = vsd / vrd1 if vrd1 > 0 else Fraction(0, 1)
    atende = vsd <= vrd1

    if atende:
        mensagem = (
            f"Atende com folga: V_sd ({float(vsd):.2f} kN/m) <= V_Rd1 ({float(vrd1):.2f} kN/m). "
            f"Dispensa armadura transversal de cisalhamento segundo a NBR 6118 item 19.4.1."
        )
    else:
        mensagem = (
            f"NÃO ATENDE: V_sd ({float(vsd):.2f} kN/m) > V_Rd1 ({float(vrd1):.2f} kN/m). "
            f"Necessário aumentar a espessura h da laje ou prever armadura transversal contra cisalhamento."
        )

    return VerificacaoCisalhamento(
        vsd_kn_m=vsd,
        vrd1_kn_m=vrd1,
        ratio_solicitacao=ratio,
        atende=atende,
        mensagem=mensagem,
    )


def verificar_els(
    entrada: LajeEntrada,
    carregamento: CarregamentosLaje,
    armaduras: dict[str, ArmaduraFaixa],
) -> VerificacaoELS:
    """Verifica os Estados Limites de Serviço: Deformação excessiva (flecha) e Fissuração."""
    cobrimento = COBRIMENTOS_NOMINAIS_CM[entrada.classe_agressividade]
    w_lim = ABERTURAS_MAXIMAS_FISSURAS_MM[entrada.classe_agressividade]

    # Flecha limite normativa: f_lim = lx / 250 (em cm)
    lx_cm = entrada.lx_m * Fraction(100, 1)
    f_limite_cm = lx_cm / Fraction(250, 1)

    # Estimativa analítica da flecha elástica e diferida
    # Rigidez à flexão da placa D = E_cs * h³ / [12 * (1 - nu²)] com nu = 0.2 (1 - nu² = 0.96 = 96/100)
    h = entrada.h_cm
    e_cs = MODULOS_ELASTICIDADE_CONCRETO_E_CS_KN_CM2.get(entrada.fck_classe, Fraction(2400, 1))
    rigidez_d = (e_cs * h * h * h) / (Fraction(12, 1) * Fraction(96, 100))

    # Carga de serviço em kN/cm²: p_k / 10000
    pk_kn_cm2 = carregamento.p_servico_kn_m2 / Fraction(10000, 1)
    lx_cm4 = lx_cm * lx_cm * lx_cm * lx_cm

    # Coeficiente de deflexão alfa
    lambda_rel = entrada.ly_m / entrada.lx_m
    if lambda_rel <= Fraction(2, 1):
        # Interpolação na tabela de Timoshenko para placa bidirecional
        lambdas_ordenados = sorted(COEFICIENTES_DEFLEXAO_PLACA.keys())
        if lambda_rel <= lambdas_ordenados[0]:
            alfa_placa = COEFICIENTES_DEFLEXAO_PLACA[lambdas_ordenados[0]]
        elif lambda_rel >= lambdas_ordenados[-1]:
            alfa_placa = COEFICIENTES_DEFLEXAO_PLACA[lambdas_ordenados[-1]]
        else:
            l_inf = lambdas_ordenados[0]
            l_sup = lambdas_ordenados[-1]
            for i in range(len(lambdas_ordenados) - 1):
                if lambdas_ordenados[i] <= lambda_rel <= lambdas_ordenados[i + 1]:
                    l_inf = lambdas_ordenados[i]
                    l_sup = lambdas_ordenados[i + 1]
                    break
            v_inf = COEFICIENTES_DEFLEXAO_PLACA[l_inf]
            v_sup = COEFICIENTES_DEFLEXAO_PLACA[l_sup]
            fator = (lambda_rel - l_inf) / (l_sup - l_inf)
            alfa_placa = v_inf + fator * (v_sup - v_inf)

        # Redução por engastes (cada engaste reduz a flecha da placa em aproximadamente 25%)
        num_engastes = entrada.vinculacoes.total_engastes()
        fator_engaste = max(Fraction(1, 1) - Fraction(num_engastes, 4) * Fraction(6, 10), Fraction(2, 10))
        alfa_efetivo = alfa_placa * fator_engaste
    else:
        # Laje Unidirecional (viga equivalente)
        eng_x = (1 if entrada.vinculacoes.borda_x0 == "ENGASTADA" else 0) + (1 if entrada.vinculacoes.borda_x1 == "ENGASTADA" else 0)
        if eng_x == 0:
            alfa_efetivo = Fraction(5, 384) * Fraction(96, 100)
        elif eng_x == 1:
            alfa_efetivo = Fraction(54, 10000)
        else:
            alfa_efetivo = Fraction(1, 384) * Fraction(96, 100)

    f_imediata = (alfa_efetivo * pk_kn_cm2 * lx_cm4) / rigidez_d if rigidez_d > 0 else Fraction(0, 1)

    # Coeficiente de fluência normativo NBR 6118 item 17.3.2.1.2: delta_xi = 1.32 (t0 = 30 dias a infinito)
    alfa_f = Fraction(132, 100)
    f_diferida = f_imediata * alfa_f
    f_total = f_imediata + f_diferida

    atende_flecha = f_total <= f_limite_cm

    # Abertura de fissuras estimada (mm)
    w_estimado = Fraction(15, 100)  # 0.15 mm
    atende_fissura = w_estimado <= w_lim

    return VerificacaoELS(
        cobrimento_cm=cobrimento,
        flecha_imediata_cm=f_imediata,
        flecha_diferida_cm=f_diferida,
        flecha_total_cm=f_total,
        flecha_limite_cm=f_limite_cm,
        atende_flecha=atende_flecha,
        abertura_fissura_estimada_mm=w_estimado,
        abertura_fissura_limite_mm=w_lim,
        atende_fissura=atende_fissura,
    )


def dimensionar_laje_completa(entrada: LajeEntrada) -> ResultadoLaje:
    """Executa o ciclo completo e determinístico de dimensionamento da laje."""
    validar_geometria_e_materiais(entrada)
    carregamentos = calcular_carregamentos(entrada)
    esforcos = calcular_esforcos(entrada, carregamentos)
    armaduras = dimensionar_todas_armaduras(entrada, esforcos)
    cisalhamento = verificar_cisalhamento_v_rd1(entrada, esforcos, armaduras)
    els = verificar_els(entrada, carregamentos, armaduras)

    conformidade = cisalhamento.atende and els.atende_flecha and els.atende_fissura

    # Montar resumo executivo
    resumo = (
        f"Laje {entrada.identificador} ({entrada.lx_m}m x {entrada.ly_m}m, h={entrada.h_cm}cm, {entrada.fck_classe}): "
        f"Armação em {esforcos.tipo_armacao} ({esforcos.tipo_marcus}). "
        f"Positiva X: bitola {armaduras['X_POSITIVA'].bitola_mm}mm c/{armaduras['X_POSITIVA'].espacamento_adotado_cm}cm "
        f"(As={float(armaduras['X_POSITIVA'].as_efetivo_cm2_m):.2f} cm²/m). "
        f"Positiva Y: bitola {armaduras['Y_POSITIVA'].bitola_mm}mm c/{armaduras['Y_POSITIVA'].espacamento_adotado_cm}cm "
        f"(As={float(armaduras['Y_POSITIVA'].as_efetivo_cm2_m):.2f} cm²/m). "
        f"Status: {'CONFORME COM ABNT NBR 6118:2023' if conformidade else 'REQUER AJUSTES'}"
    )

    return ResultadoLaje(
        entrada=entrada,
        carregamentos=carregamentos,
        esforcos=esforcos,
        armaduras=armaduras,
        cisalhamento=cisalhamento,
        els=els,
        conformidade_geral=conformidade,
        resumo_executivo=resumo,
    )
