"""Pacote de dimensionamento e verificação analítica de lajes maciças (ABNT NBR 6118:2023).

Desenvolvido segundo as diretrizes de engenharia de software da LOFRANO TECNOLOGIA:
- 100% Python puro (sem dependências externas).
- Zero floats no núcleo de cálculo (frações exatas Fraction e grandezas inteiras).
- Codecs canônicos JSON protegidos contra BOM, floats e chaves duplicadas.
- Sanitização de CSV contra injeção de fórmulas.
- Empacotamento determinístico ZIP.
"""

from .calculator import (
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
from .codecs import (
    carregar_json_canonico,
    entrada_de_dict,
    fracao_para_dict,
    parsear_fracao,
    resultado_para_dict,
    salvar_json_canonico,
)
from .constants import (
    ABERTURAS_MAXIMAS_FISSURAS_MM,
    ARMADURA_SECUNDARIA_MINIMA_ABSOLUTA_CM2_M,
    BITOLAS_COMERCIAIS_LAJES,
    CLASSES_CONCRETO_F_CK,
    COBRIMENTOS_NOMINAIS_CM,
    ESPACAMENTO_MAXIMO_PRINCIPAL_ABSOLUTO_CM,
    ESPACAMENTO_MAXIMO_SECUNDARIA_ABSOLUTO_CM,
    ESPACAMENTO_MINIMO_ABSOLUTO_CM,
    ESPESSURAS_MINIMAS_USO_CM,
    F_YD_CA50_KN_CM2,
    F_YK_CA50_KN_CM2,
    GAMMA_C,
    GAMMA_F,
    GAMMA_S,
    LARGURA_FAIXA_CALCULO_CM,
    MODULO_ELASTICIDADE_ACO_KN_CM2,
    PESO_ESPECIFICO_CONCRETO_ARMADO,
    TABELA_MARCUS_COEFICIENTES,
    TAXAS_MINIMAS_ARMADURA_RHO,
)
from .exporters import (
    exportar_csv,
    exportar_relatorio_texto,
    exportar_zip_deterministico,
    sanitizar_campo_csv,
)
from .models import (
    ArmaduraFaixa,
    CarregamentosLaje,
    EsforcosLaje,
    LajeEntrada,
    ResultadoLaje,
    TipoArmacao,
    TipoVinculacao,
    VerificacaoCisalhamento,
    VerificacaoELS,
    VinculacoesBordas,
)
from .svg_generator import gerar_painel_svg

__version__ = "1.0.0"
__author__ = "Lofrano Tecnologia"

__all__ = [
    "__version__",
    "__author__",
    "LajeEntrada",
    "VinculacoesBordas",
    "CarregamentosLaje",
    "EsforcosLaje",
    "ArmaduraFaixa",
    "VerificacaoCisalhamento",
    "VerificacaoELS",
    "ResultadoLaje",
    "TipoVinculacao",
    "TipoArmacao",
    "raiz_quadrada_fracao",
    "validar_geometria_e_materiais",
    "calcular_carregamentos",
    "determinar_tipo_marcus",
    "interpolar_coeficientes_marcus",
    "calcular_esforcos",
    "dimensionar_armadura_faixa",
    "dimensionar_todas_armaduras",
    "verificar_cisalhamento_v_rd1",
    "verificar_els",
    "dimensionar_laje_completa",
    "carregar_json_canonico",
    "salvar_json_canonico",
    "entrada_de_dict",
    "resultado_para_dict",
    "parsear_fracao",
    "fracao_para_dict",
    "exportar_relatorio_texto",
    "exportar_csv",
    "exportar_zip_deterministico",
    "sanitizar_campo_csv",
    "gerar_painel_svg",
    "GAMMA_C",
    "GAMMA_S",
    "GAMMA_F",
    "PESO_ESPECIFICO_CONCRETO_ARMADO",
    "LARGURA_FAIXA_CALCULO_CM",
    "F_YK_CA50_KN_CM2",
    "F_YD_CA50_KN_CM2",
    "MODULO_ELASTICIDADE_ACO_KN_CM2",
    "CLASSES_CONCRETO_F_CK",
    "TAXAS_MINIMAS_ARMADURA_RHO",
    "COBRIMENTOS_NOMINAIS_CM",
    "ABERTURAS_MAXIMAS_FISSURAS_MM",
    "ESPESSURAS_MINIMAS_USO_CM",
    "BITOLAS_COMERCIAIS_LAJES",
    "ESPACAMENTO_MINIMO_ABSOLUTO_CM",
    "ESPACAMENTO_MAXIMO_PRINCIPAL_ABSOLUTO_CM",
    "ESPACAMENTO_MAXIMO_SECUNDARIA_ABSOLUTO_CM",
    "ARMADURA_SECUNDARIA_MINIMA_ABSOLUTA_CM2_M",
    "TABELA_MARCUS_COEFICIENTES",
]
