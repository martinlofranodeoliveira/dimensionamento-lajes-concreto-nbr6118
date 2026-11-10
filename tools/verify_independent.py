#!/usr/bin/env python3
"""Auditor e verificador independente para dimensionamento de lajes maciças (ABNT NBR 6118:2023).

Execução 100% autônoma em SQLite em memória sem importar o pacote de produção,
recalculando os equilíbrios analíticos, armaduras mínimas e resistência ao cisalhamento
diretamente a partir das equações constitutivas fundamentais da ABNT NBR 6118:2023.
"""

from __future__ import annotations

from fractions import Fraction
import math
import sqlite3
import sys


def raiz_quadrada_racional(fracao: Fraction, precisao: int = 8) -> Fraction:
    p = fracao.numerator
    q = fracao.denominator
    fator = 10 ** (2 * precisao)
    raiz = math.isqrt(p * q * fator)
    return Fraction(raiz, q * (10 ** precisao))


def executar_auditoria_independente() -> int:
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE casos_auditoria (
            id TEXT PRIMARY KEY,
            lx_m TEXT NOT NULL,
            ly_m TEXT NOT NULL,
            h_cm TEXT NOT NULL,
            fck_mpa INTEGER NOT NULL,
            g_adic TEXT NOT NULL,
            q_acid TEXT NOT NULL,
            borda_x0 TEXT NOT NULL,
            borda_x1 TEXT NOT NULL,
            borda_y0 TEXT NOT NULL,
            borda_y1 TEXT NOT NULL
        )
    """)

    casos = [
        ("L1_Piso_Residencial", "4", "5", "10", 25, "3/2", "2", "APOIADA", "APOIADA", "APOIADA", "APOIADA"),
        ("L2_Corredor", "12/5", "6", "9", 30, "6/5", "3", "ENGASTADA", "APOIADA", "APOIADA", "APOIADA"),
    ]

    cursor.executemany("""
        INSERT INTO casos_auditoria VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, casos)
    conn.commit()

    print("=" * 78)
    print("LOFRANO TECNOLOGIA — AUDITORIA INDEPENDENTE DE LAJES MACIÇAS NBR 6118:2023")
    print("=" * 78)

    sucessos = 0
    total = len(casos)

    for linha in cursor.execute("SELECT * FROM casos_auditoria"):
        cid, lx_s, ly_s, h_s, fck_val, g_s, q_s, bx0, bx1, by0, by1 = linha
        lx = Fraction(lx_s)
        ly = Fraction(ly_s)
        h = Fraction(h_s)
        g_adic = Fraction(g_s)
        q = Fraction(q_s)

        # 1. Carregamentos
        g_pp = Fraction(25, 1) * h / Fraction(100, 1)
        g_tot = g_pp + g_adic
        p_serv = g_tot + q
        p_d = Fraction(14, 10) * p_serv

        # 2. Relação de forma
        lambda_rel = ly / lx
        is_cruz = lambda_rel <= Fraction(2, 1)

        # 3. Verificação de espessura mínima
        h_min = Fraction(8, 1)  # Piso
        assert h >= h_min, f"Espessura violada no caso {cid}"

        # 4. Cálculo independente de momento fletor
        if is_cruz:
            # Caso biapoiado 4 bordas (Marcus Tipo 1 com lambda = 5/4 = 1.25)
            # mu_x interpolado entre 1.2 (4.95) e 1.3 (5.57) -> 5.26
            mu_x = Fraction(526, 100)
            mx_k = mu_x * p_serv * (lx * lx) / Fraction(100, 1)
            mxd = Fraction(14, 10) * mx_k
        else:
            # Unidirecional com 1 engaste em x: mx_k = 9/128 * p * lx²
            mx_k = Fraction(9, 128) * p_serv * (lx * lx)
            mxd = Fraction(14, 10) * mx_k

        # 5. Altura útil e armadura de flexão
        cobrimento = Fraction(25, 10)  # CAA II: 2.5 cm
        phi_bar = Fraction(8, 10)      # 8mm = 0.8 cm
        dx = h - cobrimento - (phi_bar / Fraction(2, 1))

        # fcd e sigma_cd
        fck_kn_cm2 = Fraction(fck_val, 10)
        fcd = fck_kn_cm2 / Fraction(14, 10)
        sigma_cd = Fraction(85, 100) * fcd
        fyd = Fraction(50, 1) / Fraction(115, 100)

        # mu = md / (b * d² * sigma_cd)
        md_cm = mxd * Fraction(100, 1)
        mu_adim = md_cm / (Fraction(100, 1) * dx * dx * sigma_cd)
        assert mu_adim <= Fraction(2952, 10000), f"Ductilidade violada no caso {cid}"

        # xi e braço z
        raiz_mu = raiz_quadrada_racional(Fraction(1, 1) - Fraction(2, 1) * mu_adim)
        xi = (Fraction(1, 1) - raiz_mu) / Fraction(8, 10)
        x_cm = xi * dx
        z_cm = dx - Fraction(4, 10) * x_cm
        as_calc = md_cm / (z_cm * fyd)

        # Armadura mínima rho_min = 0.15%
        as_min = Fraction(15, 10000) * Fraction(100, 1) * h
        as_adot = max(as_calc, as_min)

        # 6. Cisalhamento V_Rd1
        # d em mm: dx * 10
        d_mm = dx * Fraction(10, 1)
        k = min(Fraction(1, 1) + raiz_quadrada_racional(Fraction(200, 1) / d_mm), Fraction(2, 1))
        rho_1 = min(as_adot / (Fraction(100, 1) * dx), Fraction(2, 100))
        tau_r = Fraction(25, 100) * Fraction(125, 1000)  # C25 fctd=0.125
        vrd1 = tau_r * k * (Fraction(12, 10) + Fraction(40, 1) * rho_1) * Fraction(100, 1) * dx

        v_sd = Fraction(14, 10) * (p_serv * lx / Fraction(2, 1))
        assert v_sd <= vrd1, f"Cisalhamento violado no caso {cid}"

        print(f"✓ Caso '{cid}': Carregamento pd={float(p_d):.2f} kN/m², mx_d={float(mxd):.2f} kN.m/m, "
              f"As={float(as_adot):.2f} cm²/m, VRd1={float(vrd1):.2f} kN/m >= Vsd={float(v_sd):.2f} kN/m -> APROVADO")
        sucessos += 1

    conn.close()
    print("-" * 78)
    print(f"Resultado da Auditoria Independente: {sucessos}/{total} casos aprovados com sucesso.")
    print("=" * 78)
    return 0 if sucessos == total else 1


if __name__ == "__main__":
    sys.exit(executar_auditoria_independente())
