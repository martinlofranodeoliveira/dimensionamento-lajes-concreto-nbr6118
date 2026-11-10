"""Constantes e tabelas normativas para dimensionamento de lajes maciças (ABNT NBR 6118:2023).

Todas as constantes utilizam tipos inteiros ou frações exatas (Fraction),
garantindo zero imprecisão de ponto flutuante em conformidade com o padrão LOFRANO TECNOLOGIA.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Final

# Coeficientes de ponderação das ações e resistências (ABNT NBR 6118:2023)
GAMMA_C: Final[Fraction] = Fraction(14, 10)     # Majoração/minoração do concreto: 1.40
GAMMA_S: Final[Fraction] = Fraction(115, 100)   # Minoração do aço estrutural: 1.15
GAMMA_F: Final[Fraction] = Fraction(14, 10)     # Majoração das ações em ELU: 1.40

# Peso específico do concreto armado (kN/m³)
PESO_ESPECIFICO_CONCRETO_ARMADO: Final[Fraction] = Fraction(25, 1)

# Largura unitária padrão de cálculo para lajes (cm)
LARGURA_FAIXA_CALCULO_CM: Final[Fraction] = Fraction(100, 1)

# Aço CA-50: f_yk = 50 kN/cm² (500 MPa), E_s = 21000 kN/cm²
F_YK_CA50_KN_CM2: Final[Fraction] = Fraction(50, 1)
F_YD_CA50_KN_CM2: Final[Fraction] = F_YK_CA50_KN_CM2 / GAMMA_S  # 50 / 1.15 = 1000/23 kN/cm²
MODULO_ELASTICIDADE_ACO_KN_CM2: Final[Fraction] = Fraction(21000, 1)

# Tabela de resistências do concreto à compressão (f_ck em MPa e kN/cm²)
# 1 MPa = 0.1 kN/cm²
CLASSES_CONCRETO_F_CK: Final[dict[str, Fraction]] = {
    "C20": Fraction(20, 10),   # 2.0 kN/cm²
    "C25": Fraction(25, 10),   # 2.5 kN/cm²
    "C30": Fraction(30, 10),   # 3.0 kN/cm²
    "C35": Fraction(35, 10),   # 3.5 kN/cm²
    "C40": Fraction(40, 10),   # 4.0 kN/cm²
    "C45": Fraction(45, 10),   # 4.5 kN/cm²
    "C50": Fraction(50, 10),   # 5.0 kN/cm²
}

# Taxas mínimas de armadura de flexão para lajes (Tabela 17.3 da NBR 6118:2023)
# Percentuais sobre a seção de concreto: rho_min = As_min / (b * h)
TAXAS_MINIMAS_ARMADURA_RHO: Final[dict[str, Fraction]] = {
    "C20": Fraction(150, 100000),   # 0.150%
    "C25": Fraction(150, 100000),   # 0.150%
    "C30": Fraction(150, 100000),   # 0.150%
    "C35": Fraction(164, 100000),   # 0.164%
    "C40": Fraction(179, 100000),   # 0.179%
    "C45": Fraction(194, 100000),   # 0.194%
    "C50": Fraction(208, 100000),   # 0.208%
}

# Cobrimento nominal mínimo conforme Classe de Agressividade Ambiental (CAA) - Tabela 7.2 (cm)
COBRIMENTOS_NOMINAIS_CM: Final[dict[str, Fraction]] = {
    "CAA_I": Fraction(20, 10),    # 2.0 cm (Fraca / Rural)
    "CAA_II": Fraction(25, 10),   # 2.5 cm (Moderada / Urbana)
    "CAA_III": Fraction(35, 10),  # 3.5 cm (Forte / Marinha / Industrial)
    "CAA_IV": Fraction(45, 10),   # 4.5 cm (Muito Forte / Respingos de maré)
}

# Aberturas máximas características de fissuras w_lim em mm (Tabela 13.4 NBR 6118)
ABERTURAS_MAXIMAS_FISSURAS_MM: Final[dict[str, Fraction]] = {
    "CAA_I": Fraction(4, 10),    # 0.4 mm
    "CAA_II": Fraction(3, 10),   # 0.3 mm
    "CAA_III": Fraction(3, 10),  # 0.3 mm
    "CAA_IV": Fraction(2, 10),   # 0.2 mm
}

# Espessuras mínimas normativas por tipo de uso (item 13.2.4.1 da NBR 6118:2023) em cm
ESPESSURAS_MINIMAS_USO_CM: Final[dict[str, Fraction]] = {
    "COBERTURA_NAO_BALANCO": Fraction(7, 1),
    "PISO_NAO_BALANCO": Fraction(8, 1),
    "BALANCO_COBERTURA": Fraction(7, 1),
    "BALANCO_PISO": Fraction(10, 1),
    "VEICULOS_LEVES": Fraction(10, 1),   # Veículos de peso total <= 30 kN
    "VEICULOS_PESADOS": Fraction(12, 1),  # Veículos de peso total > 30 kN
}

# Bitolas padronizadas de armadura para lajes comerciais (diâmetro em mm, diâmetro em cm, área em cm²)
# Área de cada barra individual calculada com pi = 314159265 / 100000000
PI_FRACAO: Final[Fraction] = Fraction(314159265, 100000000)

BITOLAS_COMERCIAIS_LAJES: Final[dict[str, dict[str, Fraction]]] = {
    "5.0": {
        "diametro_mm": Fraction(50, 10),
        "diametro_cm": Fraction(50, 100),
        "area_cm2": Fraction(1963, 10000),      # ~0.1963 cm²
    },
    "6.3": {
        "diametro_mm": Fraction(63, 10),
        "diametro_cm": Fraction(63, 100),
        "area_cm2": Fraction(3117, 10000),      # ~0.3117 cm²
    },
    "8.0": {
        "diametro_mm": Fraction(80, 10),
        "diametro_cm": Fraction(80, 100),
        "area_cm2": Fraction(5027, 10000),      # ~0.5027 cm²
    },
    "10.0": {
        "diametro_mm": Fraction(100, 10),
        "diametro_cm": Fraction(100, 100),
        "area_cm2": Fraction(7854, 10000),      # ~0.7854 cm²
    },
    "12.5": {
        "diametro_mm": Fraction(125, 10),
        "diametro_cm": Fraction(125, 100),
        "area_cm2": Fraction(12272, 10000),     # ~1.2272 cm²
    },
}

# Limites de espaçamento normativo (NBR 6118 item 20.1)
ESPACAMENTO_MINIMO_ABSOLUTO_CM: Final[Fraction] = Fraction(7, 1)
ESPACAMENTO_MAXIMO_PRINCIPAL_ABSOLUTO_CM: Final[Fraction] = Fraction(20, 1)
ESPACAMENTO_MAXIMO_SECUNDARIA_ABSOLUTO_CM: Final[Fraction] = Fraction(33, 1)

# Armadura secundária mínima absoluta (cm²/m)
ARMADURA_SECUNDARIA_MINIMA_ABSOLUTA_CM2_M: Final[Fraction] = Fraction(9, 10)  # 0.9 cm²/m

# Módulo de deformação secante do concreto E_cs (kN/cm²) - NBR 6118:2023 item 8.2.8
MODULOS_ELASTICIDADE_CONCRETO_E_CS_KN_CM2: Final[dict[str, Fraction]] = {
    "C20": Fraction(2100, 1),
    "C25": Fraction(2400, 1),
    "C30": Fraction(2700, 1),
    "C35": Fraction(2950, 1),
    "C40": Fraction(3200, 1),
    "C45": Fraction(3400, 1),
    "C50": Fraction(3600, 1),
}

# Coeficientes de deflexão de placa elástica bidirecional (Timoshenko / NBR 6118)
# w_max = alfa * (p * lx^4) / D, onde D = E_cs * h^3 / [12 * (1 - nu^2)]
COEFICIENTES_DEFLEXAO_PLACA: Final[dict[Fraction, Fraction]] = {
    Fraction(10, 10): Fraction(406, 100000),  # 0.00406
    Fraction(11, 10): Fraction(485, 100000),  # 0.00485
    Fraction(12, 10): Fraction(564, 100000),  # 0.00564
    Fraction(13, 10): Fraction(643, 100000),  # 0.00643
    Fraction(14, 10): Fraction(719, 100000),  # 0.00719
    Fraction(15, 10): Fraction(788, 100000),  # 0.00788
    Fraction(16, 10): Fraction(850, 100000),  # 0.00850
    Fraction(17, 10): Fraction(904, 100000),  # 0.00904
    Fraction(18, 10): Fraction(949, 100000),  # 0.00949
    Fraction(19, 10): Fraction(987, 100000),  # 0.00987
    Fraction(20, 10): Fraction(1017, 100000), # 0.01017
}

# Tabela de Coeficientes de Marcus (Tabelas clássicas para lajes em cruz com torção)
# Tipos:
# "TIPO_1": 4 bordas simplesmente apoiadas
# "TIPO_2A": 1 borda engastada em lx, 3 apoiadas
# "TIPO_2B": 1 borda engastada em ly, 3 apoiadas
# "TIPO_3": 2 bordas adjacentes engastadas (lx e ly) e 2 apoiadas
# "TIPO_4A": 2 bordas opostas engastadas em lx e 2 apoiadas em ly
# "TIPO_4B": 2 bordas opostas apoiadas em lx e 2 engastadas em ly
# "TIPO_5A": 2 engastadas em lx e 1 engastada em ly (3 engastadas, 1 apoiada)
# "TIPO_5B": 1 engastada em lx e 2 engastadas em ly (3 engastadas, 1 apoiada)
# "TIPO_6": 4 bordas engastadas
#
# Para cada tipo e lambda (ly/lx de 1.0 a 2.0 em passos de 0.10):
# mu_x: momento positivo mx = mu_x * p * lx² / 100
# mu_y: momento positivo my = mu_y * p * lx² / 100
# mu_xe: momento negativo m'xe = mu_xe * p * lx² / 100 (se houver engaste em lx)
# mu_ye: momento negativo m'ye = mu_ye * p * lx² / 100 (se houver engaste em ly)
# vx, vy: quinhões de reação de apoio qx, qy (kN/m)
TABELA_MARCUS_COEFICIENTES: Final[dict[str, dict[Fraction, dict[str, Fraction]]]] = {
    "TIPO_1": {
        Fraction(10, 10): {"mu_x": Fraction(367, 100), "mu_y": Fraction(367, 100), "mu_xe": Fraction(0, 1), "mu_ye": Fraction(0, 1), "qx": Fraction(25, 100), "qy": Fraction(25, 100)},
        Fraction(11, 10): {"mu_x": Fraction(431, 100), "mu_y": Fraction(356, 100), "mu_xe": Fraction(0, 1), "mu_ye": Fraction(0, 1), "qx": Fraction(29, 100), "qy": Fraction(21, 100)},
        Fraction(12, 10): {"mu_x": Fraction(495, 100), "mu_y": Fraction(344, 100), "mu_xe": Fraction(0, 1), "mu_ye": Fraction(0, 1), "qx": Fraction(33, 100), "qy": Fraction(17, 100)},
        Fraction(13, 10): {"mu_x": Fraction(557, 100), "mu_y": Fraction(330, 100), "mu_xe": Fraction(0, 1), "mu_ye": Fraction(0, 1), "qx": Fraction(36, 100), "qy": Fraction(14, 100)},
        Fraction(14, 10): {"mu_x": Fraction(616, 100), "mu_y": Fraction(315, 100), "mu_xe": Fraction(0, 1), "mu_ye": Fraction(0, 1), "qx": Fraction(39, 100), "qy": Fraction(11, 100)},
        Fraction(15, 10): {"mu_x": Fraction(672, 100), "mu_y": Fraction(299, 100), "mu_xe": Fraction(0, 1), "mu_ye": Fraction(0, 1), "qx": Fraction(42, 100), "qy": Fraction(8, 100)},
        Fraction(16, 10): {"mu_x": Fraction(724, 100), "mu_y": Fraction(283, 100), "mu_xe": Fraction(0, 1), "mu_ye": Fraction(0, 1), "qx": Fraction(44, 100), "qy": Fraction(6, 100)},
        Fraction(17, 10): {"mu_x": Fraction(772, 100), "mu_y": Fraction(267, 100), "mu_xe": Fraction(0, 1), "mu_ye": Fraction(0, 1), "qx": Fraction(45, 100), "qy": Fraction(5, 100)},
        Fraction(18, 10): {"mu_x": Fraction(816, 100), "mu_y": Fraction(252, 100), "mu_xe": Fraction(0, 1), "mu_ye": Fraction(0, 1), "qx": Fraction(46, 100), "qy": Fraction(4, 100)},
        Fraction(19, 10): {"mu_x": Fraction(856, 100), "mu_y": Fraction(237, 100), "mu_xe": Fraction(0, 1), "mu_ye": Fraction(0, 1), "qx": Fraction(47, 100), "qy": Fraction(3, 100)},
        Fraction(20, 10): {"mu_x": Fraction(893, 100), "mu_y": Fraction(223, 100), "mu_xe": Fraction(0, 1), "mu_ye": Fraction(0, 1), "qx": Fraction(48, 100), "qy": Fraction(2, 100)},
    },
    "TIPO_2A": {
        Fraction(10, 10): {"mu_x": Fraction(302, 100), "mu_y": Fraction(334, 100), "mu_xe": Fraction(734, 100), "mu_ye": Fraction(0, 1), "qx": Fraction(31, 100), "qy": Fraction(19, 100)},
        Fraction(11, 10): {"mu_x": Fraction(359, 100), "mu_y": Fraction(328, 100), "mu_xe": Fraction(826, 100), "mu_ye": Fraction(0, 1), "qx": Fraction(35, 100), "qy": Fraction(15, 100)},
        Fraction(12, 10): {"mu_x": Fraction(416, 100), "mu_y": Fraction(320, 100), "mu_xe": Fraction(913, 100), "mu_ye": Fraction(0, 1), "qx": Fraction(38, 100), "qy": Fraction(12, 100)},
        Fraction(13, 10): {"mu_x": Fraction(472, 100), "mu_y": Fraction(310, 100), "mu_xe": Fraction(993, 100), "mu_ye": Fraction(0, 1), "qx": Fraction(41, 100), "qy": Fraction(9, 100)},
        Fraction(14, 10): {"mu_x": Fraction(526, 100), "mu_y": Fraction(298, 100), "mu_xe": Fraction(1067, 100), "mu_ye": Fraction(0, 1), "qx": Fraction(43, 100), "qy": Fraction(7, 100)},
        Fraction(15, 10): {"mu_x": Fraction(578, 100), "mu_y": Fraction(285, 100), "mu_xe": Fraction(1134, 100), "mu_ye": Fraction(0, 1), "qx": Fraction(45, 100), "qy": Fraction(5, 100)},
        Fraction(16, 10): {"mu_x": Fraction(626, 100), "mu_y": Fraction(272, 100), "mu_xe": Fraction(1194, 100), "mu_ye": Fraction(0, 1), "qx": Fraction(46, 100), "qy": Fraction(4, 100)},
        Fraction(17, 10): {"mu_x": Fraction(672, 100), "mu_y": Fraction(258, 100), "mu_xe": Fraction(1248, 100), "mu_ye": Fraction(0, 1), "qx": Fraction(47, 100), "qy": Fraction(3, 100)},
        Fraction(18, 10): {"mu_x": Fraction(714, 100), "mu_y": Fraction(245, 100), "mu_xe": Fraction(1296, 100), "mu_ye": Fraction(0, 1), "qx": Fraction(48, 100), "qy": Fraction(2, 100)},
        Fraction(19, 10): {"mu_x": Fraction(753, 100), "mu_y": Fraction(232, 100), "mu_xe": Fraction(1339, 100), "mu_ye": Fraction(0, 1), "qx": Fraction(48, 100), "qy": Fraction(2, 100)},
        Fraction(20, 10): {"mu_x": Fraction(789, 100), "mu_y": Fraction(219, 100), "mu_xe": Fraction(1376, 100), "mu_ye": Fraction(0, 1), "qx": Fraction(49, 100), "qy": Fraction(1, 100)},
    },
    "TIPO_2B": {
        Fraction(10, 10): {"mu_x": Fraction(334, 100), "mu_y": Fraction(302, 100), "mu_xe": Fraction(0, 1), "mu_ye": Fraction(734, 100), "qx": Fraction(19, 100), "qy": Fraction(31, 100)},
        Fraction(11, 10): {"mu_x": Fraction(398, 100), "mu_y": Fraction(294, 100), "mu_xe": Fraction(0, 1), "mu_ye": Fraction(738, 100), "qx": Fraction(23, 100), "qy": Fraction(27, 100)},
        Fraction(12, 10): {"mu_x": Fraction(463, 100), "mu_y": Fraction(285, 100), "mu_xe": Fraction(0, 1), "mu_ye": Fraction(742, 100), "qx": Fraction(28, 100), "qy": Fraction(22, 100)},
        Fraction(13, 10): {"mu_x": Fraction(527, 100), "mu_y": Fraction(275, 100), "mu_xe": Fraction(0, 1), "mu_ye": Fraction(745, 100), "qx": Fraction(32, 100), "qy": Fraction(18, 100)},
        Fraction(14, 10): {"mu_x": Fraction(589, 100), "mu_y": Fraction(264, 100), "mu_xe": Fraction(0, 1), "mu_ye": Fraction(747, 100), "qx": Fraction(36, 100), "qy": Fraction(14, 100)},
        Fraction(15, 10): {"mu_x": Fraction(648, 100), "mu_y": Fraction(253, 100), "mu_xe": Fraction(0, 1), "mu_ye": Fraction(748, 100), "qx": Fraction(39, 100), "qy": Fraction(11, 100)},
        Fraction(16, 10): {"mu_x": Fraction(704, 100), "mu_y": Fraction(241, 100), "mu_xe": Fraction(0, 1), "mu_ye": Fraction(748, 100), "qx": Fraction(41, 100), "qy": Fraction(9, 100)},
        Fraction(17, 10): {"mu_x": Fraction(755, 100), "mu_y": Fraction(229, 100), "mu_xe": Fraction(0, 1), "mu_ye": Fraction(747, 100), "qx": Fraction(43, 100), "qy": Fraction(7, 100)},
        Fraction(18, 10): {"mu_x": Fraction(802, 100), "mu_y": Fraction(218, 100), "mu_xe": Fraction(0, 1), "mu_ye": Fraction(746, 100), "qx": Fraction(45, 100), "qy": Fraction(5, 100)},
        Fraction(19, 10): {"mu_x": Fraction(844, 100), "mu_y": Fraction(206, 100), "mu_xe": Fraction(0, 1), "mu_ye": Fraction(744, 100), "qx": Fraction(46, 100), "qy": Fraction(4, 100)},
        Fraction(20, 10): {"mu_x": Fraction(883, 100), "mu_y": Fraction(195, 100), "mu_xe": Fraction(0, 1), "mu_ye": Fraction(742, 100), "qx": Fraction(47, 100), "qy": Fraction(3, 100)},
    },
    "TIPO_3": {
        Fraction(10, 10): {"mu_x": Fraction(277, 100), "mu_y": Fraction(277, 100), "mu_xe": Fraction(686, 100), "mu_ye": Fraction(686, 100), "qx": Fraction(25, 100), "qy": Fraction(25, 100)},
        Fraction(11, 10): {"mu_x": Fraction(333, 100), "mu_y": Fraction(271, 100), "mu_xe": Fraction(773, 100), "mu_ye": Fraction(696, 100), "qx": Fraction(29, 100), "qy": Fraction(21, 100)},
        Fraction(12, 10): {"mu_x": Fraction(390, 100), "mu_y": Fraction(264, 100), "mu_xe": Fraction(859, 100), "mu_ye": Fraction(704, 100), "qx": Fraction(33, 100), "qy": Fraction(17, 100)},
        Fraction(13, 10): {"mu_x": Fraction(446, 100), "mu_y": Fraction(256, 100), "mu_xe": Fraction(941, 100), "mu_ye": Fraction(710, 100), "qx": Fraction(36, 100), "qy": Fraction(14, 100)},
        Fraction(14, 10): {"mu_x": Fraction(501, 100), "mu_y": Fraction(247, 100), "mu_xe": Fraction(1019, 100), "mu_ye": Fraction(714, 100), "qx": Fraction(39, 100), "qy": Fraction(11, 100)},
        Fraction(15, 10): {"mu_x": Fraction(554, 100), "mu_y": Fraction(237, 100), "mu_xe": Fraction(1091, 100), "mu_ye": Fraction(716, 100), "qx": Fraction(42, 100), "qy": Fraction(8, 100)},
        Fraction(16, 10): {"mu_x": Fraction(605, 100), "mu_y": Fraction(227, 100), "mu_xe": Fraction(1157, 100), "mu_ye": Fraction(717, 100), "qx": Fraction(44, 100), "qy": Fraction(6, 100)},
        Fraction(17, 10): {"mu_x": Fraction(652, 100), "mu_y": Fraction(216, 100), "mu_xe": Fraction(1217, 100), "mu_ye": Fraction(716, 100), "qx": Fraction(45, 100), "qy": Fraction(5, 100)},
        Fraction(18, 10): {"mu_x": Fraction(697, 100), "mu_y": Fraction(206, 100), "mu_xe": Fraction(1270, 100), "mu_ye": Fraction(714, 100), "qx": Fraction(46, 100), "qy": Fraction(4, 100)},
        Fraction(19, 10): {"mu_x": Fraction(738, 100), "mu_y": Fraction(196, 100), "mu_xe": Fraction(1318, 100), "mu_ye": Fraction(711, 100), "qx": Fraction(47, 100), "qy": Fraction(3, 100)},
        Fraction(20, 10): {"mu_x": Fraction(777, 100), "mu_y": Fraction(186, 100), "mu_xe": Fraction(1360, 100), "mu_ye": Fraction(708, 100), "qx": Fraction(48, 100), "qy": Fraction(2, 100)},
    },
    "TIPO_4A": {
        Fraction(10, 10): {"mu_x": Fraction(240, 100), "mu_y": Fraction(301, 100), "mu_xe": Fraction(598, 100), "mu_ye": Fraction(0, 1), "qx": Fraction(37, 100), "qy": Fraction(13, 100)},
        Fraction(11, 10): {"mu_x": Fraction(290, 100), "mu_y": Fraction(298, 100), "mu_xe": Fraction(681, 100), "mu_ye": Fraction(0, 1), "qx": Fraction(40, 100), "qy": Fraction(10, 100)},
        Fraction(12, 10): {"mu_x": Fraction(341, 100), "mu_y": Fraction(292, 100), "mu_xe": Fraction(763, 100), "mu_ye": Fraction(0, 1), "qx": Fraction(43, 100), "qy": Fraction(7, 100)},
        Fraction(13, 10): {"mu_x": Fraction(391, 100), "mu_y": Fraction(285, 100), "mu_xe": Fraction(841, 100), "mu_ye": Fraction(0, 1), "qx": Fraction(45, 100), "qy": Fraction(5, 100)},
        Fraction(14, 10): {"mu_x": Fraction(441, 100), "mu_y": Fraction(276, 100), "mu_xe": Fraction(913, 100), "mu_ye": Fraction(0, 1), "qx": Fraction(46, 100), "qy": Fraction(4, 100)},
        Fraction(15, 10): {"mu_x": Fraction(489, 100), "mu_y": Fraction(266, 100), "mu_xe": Fraction(980, 100), "mu_ye": Fraction(0, 1), "qx": Fraction(47, 100), "qy": Fraction(3, 100)},
        Fraction(16, 10): {"mu_x": Fraction(535, 100), "mu_y": Fraction(256, 100), "mu_xe": Fraction(1041, 100), "mu_ye": Fraction(0, 1), "qx": Fraction(48, 100), "qy": Fraction(2, 100)},
        Fraction(17, 10): {"mu_x": Fraction(579, 100), "mu_y": Fraction(245, 100), "mu_xe": Fraction(1096, 100), "mu_ye": Fraction(0, 1), "qx": Fraction(48, 100), "qy": Fraction(2, 100)},
        Fraction(18, 10): {"mu_x": Fraction(620, 100), "mu_y": Fraction(234, 100), "mu_xe": Fraction(1146, 100), "mu_ye": Fraction(0, 1), "qx": Fraction(49, 100), "qy": Fraction(1, 100)},
        Fraction(19, 10): {"mu_x": Fraction(659, 100), "mu_y": Fraction(223, 100), "mu_xe": Fraction(1191, 100), "mu_ye": Fraction(0, 1), "qx": Fraction(49, 100), "qy": Fraction(1, 100)},
        Fraction(20, 10): {"mu_x": Fraction(696, 100), "mu_y": Fraction(212, 100), "mu_xe": Fraction(1231, 100), "mu_ye": Fraction(0, 1), "qx": Fraction(50, 100), "qy": Fraction(0, 1)},
    },
    "TIPO_4B": {
        Fraction(10, 10): {"mu_x": Fraction(301, 100), "mu_y": Fraction(240, 100), "mu_xe": Fraction(0, 1), "mu_ye": Fraction(598, 100), "qx": Fraction(13, 100), "qy": Fraction(37, 100)},
        Fraction(11, 10): {"mu_x": Fraction(365, 100), "mu_y": Fraction(237, 100), "mu_xe": Fraction(0, 1), "mu_ye": Fraction(612, 100), "qx": Fraction(17, 100), "qy": Fraction(33, 100)},
        Fraction(12, 10): {"mu_x": Fraction(431, 100), "mu_y": Fraction(233, 100), "mu_xe": Fraction(0, 1), "mu_ye": Fraction(624, 100), "qx": Fraction(22, 100), "qy": Fraction(28, 100)},
        Fraction(13, 10): {"mu_x": Fraction(497, 100), "mu_y": Fraction(228, 100), "mu_xe": Fraction(0, 1), "mu_ye": Fraction(633, 100), "qx": Fraction(26, 100), "qy": Fraction(24, 100)},
        Fraction(14, 10): {"mu_x": Fraction(561, 100), "mu_y": Fraction(221, 100), "mu_xe": Fraction(0, 1), "mu_ye": Fraction(640, 100), "qx": Fraction(30, 100), "qy": Fraction(20, 100)},
        Fraction(15, 10): {"mu_x": Fraction(623, 100), "mu_y": Fraction(214, 100), "mu_xe": Fraction(0, 1), "mu_ye": Fraction(645, 100), "qx": Fraction(34, 100), "qy": Fraction(16, 100)},
        Fraction(16, 10): {"mu_x": Fraction(681, 100), "mu_y": Fraction(206, 100), "mu_xe": Fraction(0, 1), "mu_ye": Fraction(649, 100), "qx": Fraction(37, 100), "qy": Fraction(13, 100)},
        Fraction(17, 10): {"mu_x": Fraction(736, 100), "mu_y": Fraction(197, 100), "mu_xe": Fraction(0, 1), "mu_ye": Fraction(652, 100), "qx": Fraction(39, 100), "qy": Fraction(11, 100)},
        Fraction(18, 10): {"mu_x": Fraction(787, 100), "mu_y": Fraction(189, 100), "mu_xe": Fraction(0, 1), "mu_ye": Fraction(654, 100), "qx": Fraction(41, 100), "qy": Fraction(9, 100)},
        Fraction(19, 10): {"mu_x": Fraction(833, 100), "mu_y": Fraction(180, 100), "mu_xe": Fraction(0, 1), "mu_ye": Fraction(655, 100), "qx": Fraction(43, 100), "qy": Fraction(7, 100)},
        Fraction(20, 10): {"mu_x": Fraction(875, 100), "mu_y": Fraction(172, 100), "mu_xe": Fraction(0, 1), "mu_ye": Fraction(655, 100), "qx": Fraction(44, 100), "qy": Fraction(6, 100)},
    },
    "TIPO_5A": {
        Fraction(10, 10): {"mu_x": Fraction(224, 100), "mu_y": Fraction(249, 100), "mu_xe": Fraction(567, 100), "mu_ye": Fraction(633, 100), "qx": Fraction(31, 100), "qy": Fraction(19, 100)},
        Fraction(11, 10): {"mu_x": Fraction(273, 100), "mu_y": Fraction(246, 100), "mu_xe": Fraction(648, 100), "mu_ye": Fraction(649, 100), "qx": Fraction(35, 100), "qy": Fraction(15, 100)},
        Fraction(12, 10): {"mu_x": Fraction(323, 100), "mu_y": Fraction(242, 100), "mu_xe": Fraction(727, 100), "mu_ye": Fraction(661, 100), "qx": Fraction(38, 100), "qy": Fraction(12, 100)},
        Fraction(13, 10): {"mu_x": Fraction(373, 100), "mu_y": Fraction(236, 100), "mu_xe": Fraction(803, 100), "mu_ye": Fraction(671, 100), "qx": Fraction(41, 100), "qy": Fraction(9, 100)},
        Fraction(14, 10): {"mu_x": Fraction(423, 100), "mu_y": Fraction(230, 100), "mu_xe": Fraction(874, 100), "mu_ye": Fraction(678, 100), "qx": Fraction(43, 100), "qy": Fraction(7, 100)},
        Fraction(15, 10): {"mu_x": Fraction(471, 100), "mu_y": Fraction(222, 100), "mu_xe": Fraction(941, 100), "mu_ye": Fraction(683, 100), "qx": Fraction(45, 100), "qy": Fraction(5, 100)},
        Fraction(16, 10): {"mu_x": Fraction(517, 100), "mu_y": Fraction(214, 100), "mu_xe": Fraction(1003, 100), "mu_ye": Fraction(687, 100), "qx": Fraction(46, 100), "qy": Fraction(4, 100)},
        Fraction(17, 10): {"mu_x": Fraction(561, 100), "mu_y": Fraction(206, 100), "mu_xe": Fraction(1060, 100), "mu_ye": Fraction(689, 100), "qx": Fraction(47, 100), "qy": Fraction(3, 100)},
        Fraction(18, 10): {"mu_x": Fraction(603, 100), "mu_y": Fraction(198, 100), "mu_xe": Fraction(1111, 100), "mu_ye": Fraction(689, 100), "qx": Fraction(48, 100), "qy": Fraction(2, 100)},
        Fraction(19, 10): {"mu_x": Fraction(643, 100), "mu_y": Fraction(189, 100), "mu_xe": Fraction(1159, 100), "mu_ye": Fraction(689, 100), "qx": Fraction(48, 100), "qy": Fraction(2, 100)},
        Fraction(20, 10): {"mu_x": Fraction(680, 100), "mu_y": Fraction(181, 100), "mu_xe": Fraction(1201, 100), "mu_ye": Fraction(688, 100), "qx": Fraction(49, 100), "qy": Fraction(1, 100)},
    },
    "TIPO_5B": {
        Fraction(10, 10): {"mu_x": Fraction(249, 100), "mu_y": Fraction(224, 100), "mu_xe": Fraction(633, 100), "mu_ye": Fraction(567, 100), "qx": Fraction(19, 100), "qy": Fraction(31, 100)},
        Fraction(11, 10): {"mu_x": Fraction(306, 100), "mu_y": Fraction(221, 100), "mu_xe": Fraction(720, 100), "mu_ye": Fraction(582, 100), "qx": Fraction(23, 100), "qy": Fraction(27, 100)},
        Fraction(12, 10): {"mu_x": Fraction(364, 100), "mu_y": Fraction(218, 100), "mu_xe": Fraction(803, 100), "mu_ye": Fraction(595, 100), "qx": Fraction(28, 100), "qy": Fraction(22, 100)},
        Fraction(13, 10): {"mu_x": Fraction(421, 100), "mu_y": Fraction(214, 100), "mu_xe": Fraction(883, 100), "mu_ye": Fraction(605, 100), "qx": Fraction(32, 100), "qy": Fraction(18, 100)},
        Fraction(14, 10): {"mu_x": Fraction(478, 100), "mu_y": Fraction(209, 100), "mu_xe": Fraction(957, 100), "mu_ye": Fraction(613, 100), "qx": Fraction(36, 100), "qy": Fraction(14, 100)},
        Fraction(15, 10): {"mu_x": Fraction(533, 100), "mu_y": Fraction(203, 100), "mu_xe": Fraction(1027, 100), "mu_ye": Fraction(620, 100), "qx": Fraction(39, 100), "qy": Fraction(11, 100)},
        Fraction(16, 10): {"mu_x": Fraction(586, 100), "mu_y": Fraction(196, 100), "mu_xe": Fraction(1091, 100), "mu_ye": Fraction(624, 100), "qx": Fraction(41, 100), "qy": Fraction(9, 100)},
        Fraction(17, 10): {"mu_x": Fraction(636, 100), "mu_y": Fraction(189, 100), "mu_xe": Fraction(1150, 100), "mu_ye": Fraction(627, 100), "qx": Fraction(43, 100), "qy": Fraction(7, 100)},
        Fraction(18, 10): {"mu_x": Fraction(683, 100), "mu_y": Fraction(181, 100), "mu_xe": Fraction(1203, 100), "mu_ye": Fraction(629, 100), "qx": Fraction(45, 100), "qy": Fraction(5, 100)},
        Fraction(19, 10): {"mu_x": Fraction(727, 100), "mu_y": Fraction(174, 100), "mu_xe": Fraction(1251, 100), "mu_ye": Fraction(630, 100), "qx": Fraction(46, 100), "qy": Fraction(4, 100)},
        Fraction(20, 10): {"mu_x": Fraction(767, 100), "mu_y": Fraction(166, 100), "mu_xe": Fraction(1294, 100), "mu_ye": Fraction(630, 100), "qx": Fraction(47, 100), "qy": Fraction(3, 100)},
    },
    "TIPO_6": {
        Fraction(10, 10): {"mu_x": Fraction(207, 100), "mu_y": Fraction(207, 100), "mu_xe": Fraction(526, 100), "mu_ye": Fraction(526, 100), "qx": Fraction(25, 100), "qy": Fraction(25, 100)},
        Fraction(11, 10): {"mu_x": Fraction(254, 100), "mu_y": Fraction(205, 100), "mu_xe": Fraction(605, 100), "mu_ye": Fraction(541, 100), "qx": Fraction(29, 100), "qy": Fraction(21, 100)},
        Fraction(12, 10): {"mu_x": Fraction(303, 100), "mu_y": Fraction(202, 100), "mu_xe": Fraction(683, 100), "mu_ye": Fraction(554, 100), "qx": Fraction(33, 100), "qy": Fraction(17, 100)},
        Fraction(13, 10): {"mu_x": Fraction(352, 100), "mu_y": Fraction(198, 100), "mu_xe": Fraction(758, 100), "mu_ye": Fraction(565, 100), "qx": Fraction(36, 100), "qy": Fraction(14, 100)},
        Fraction(14, 10): {"mu_x": Fraction(401, 100), "mu_y": Fraction(193, 100), "mu_xe": Fraction(830, 100), "mu_ye": Fraction(573, 100), "qx": Fraction(39, 100), "qy": Fraction(11, 100)},
        Fraction(15, 10): {"mu_x": Fraction(448, 100), "mu_y": Fraction(187, 100), "mu_xe": Fraction(897, 100), "mu_ye": Fraction(579, 100), "qx": Fraction(42, 100), "qy": Fraction(8, 100)},
        Fraction(16, 10): {"mu_x": Fraction(494, 100), "mu_y": Fraction(181, 100), "mu_xe": Fraction(959, 100), "mu_ye": Fraction(584, 100), "qx": Fraction(44, 100), "qy": Fraction(6, 100)},
        Fraction(17, 10): {"mu_x": Fraction(538, 100), "mu_y": Fraction(175, 100), "mu_xe": Fraction(1016, 100), "mu_ye": Fraction(587, 100), "qx": Fraction(45, 100), "qy": Fraction(5, 100)},
        Fraction(18, 10): {"mu_x": Fraction(580, 100), "mu_y": Fraction(168, 100), "mu_xe": Fraction(1067, 100), "mu_ye": Fraction(588, 100), "qx": Fraction(46, 100), "qy": Fraction(4, 100)},
        Fraction(19, 10): {"mu_x": Fraction(619, 100), "mu_y": Fraction(162, 100), "mu_xe": Fraction(1114, 100), "mu_ye": Fraction(589, 100), "qx": Fraction(47, 100), "qy": Fraction(3, 100)},
        Fraction(20, 10): {"mu_x": Fraction(656, 100), "mu_y": Fraction(155, 100), "mu_xe": Fraction(1156, 100), "mu_ye": Fraction(588, 100), "qx": Fraction(48, 100), "qy": Fraction(2, 100)},
    },
}
