import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


# ============================================================
# CONFIGURAÇÃO
# ============================================================

PASTA_PROJETO = Path(__file__).resolve().parent

ARQUIVO_ANALISE = (
    PASTA_PROJETO
    / "outputs"
    / "mercado_analise.csv"
)

PASTA_GRAFICOS = (
    PASTA_PROJETO
    / "outputs"
    / "graficos"
)

PASTA_GRAFICOS.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# CONFIGURAÇÃO VISUAL
# ============================================================

TAMANHO_TITULO = 20
TAMANHO_SUBTITULO = 12
TAMANHO_EIXO = 11
TAMANHO_ROTULO = 10

plt.rcParams.update({
    "font.size": TAMANHO_EIXO,
    "axes.titlesize": TAMANHO_TITULO,
    "axes.labelsize": TAMANHO_EIXO,
    "xtick.labelsize": TAMANHO_EIXO,
    "ytick.labelsize": TAMANHO_EIXO,
    "figure.dpi": 120,
    "savefig.dpi": 180
})


# ============================================================
# CARREGAR BASE
# ============================================================

print("=" * 70)
print("GERAÇÃO DOS GRÁFICOS — FOOD SERVICE")
print("=" * 70)

df = pd.read_csv(
    ARQUIVO_ANALISE,
    encoding="utf-8-sig"
)

print(
    f"\nBase carregada: "
    f"{len(df):,} municípios"
)


# ============================================================
# PREPARAÇÃO
# ============================================================

df["municipio_label"] = (
    df["municipio"].astype(str)
    + " — "
    + df["uf"].astype(str)
)

df["estabelecimentos_recentes"] = pd.to_numeric(
    df["estabelecimentos_recentes"],
    errors="coerce"
)

df["taxa_recencia"] = pd.to_numeric(
    df["taxa_recencia"],
    errors="coerce"
)

df["estabelecimentos_food_service"] = pd.to_numeric(
    df["estabelecimentos_food_service"],
    errors="coerce"
)

df["taxa_porte_maior"] = pd.to_numeric(
    df["taxa_porte_maior"],
    errors="coerce"
)


# ============================================================
# FUNÇÃO DE TÍTULO
# ============================================================

def adicionar_titulo(ax, titulo, subtitulo):

    ax.set_title(
        titulo,
        fontsize=TAMANHO_TITULO,
        fontweight="bold",
        loc="left",
        pad=28
    )

    ax.text(
        0,
        1.015,
        subtitulo,
        transform=ax.transAxes,
        fontsize=TAMANHO_SUBTITULO,
        va="bottom",
        ha="left"
    )


# ============================================================
# 1. CONCENTRAÇÃO DO MERCADO
# ============================================================

print("\n[1/5] Gerando concentração do mercado...")

top15 = (
    df
    .nlargest(
        15,
        "estabelecimentos_food_service"
    )
    .copy()
)


fig, ax = plt.subplots(
    figsize=(12, 9)
)


barras = ax.barh(
    top15["municipio_label"],
    top15["estabelecimentos_food_service"]
)


for barra, valor in zip(
    barras,
    top15["estabelecimentos_food_service"]
):

    ax.text(
        barra.get_width()
        + top15[
            "estabelecimentos_food_service"
        ].max() * 0.008,

        barra.get_y()
        + barra.get_height() / 2,

        f"{valor:,.0f}".replace(",", "."),

        va="center",
        fontsize=TAMANHO_ROTULO
    )


adicionar_titulo(
    ax,
    "Onde está concentrado o mercado de Food Service?",
    "Quantidade de estabelecimentos Food Service ativos por município — 2026"
)


ax.set_xlabel(
    "Estabelecimentos ativos"
)


ax.invert_yaxis()


ax.spines[
    ["top", "right", "left"]
].set_visible(False)


ax.grid(
    axis="x",
    alpha=0.2
)


ax.set_axisbelow(True)


plt.tight_layout(
    rect=[0, 0, 1, 0.94]
)


plt.savefig(
    PASTA_GRAFICOS / "01_top_mercados_escala.png",
    bbox_inches="tight"
)


plt.close()


# ============================================================
# 2. DINÂMICA RECENTE
# ============================================================

print("\n[2/5] Gerando dinâmica recente...")

top15_recencia = (
    df[
        df["estabelecimentos_food_service"] >= 500
    ]
    .nlargest(
        15,
        "taxa_recencia"
    )
    .copy()
)


fig, ax = plt.subplots(
    figsize=(12, 9)
)


barras = ax.barh(
    top15_recencia["municipio_label"],
    top15_recencia["taxa_recencia"]
)


for barra, valor in zip(
    barras,
    top15_recencia["taxa_recencia"]
):

    ax.text(
        barra.get_width() + 0.8,

        barra.get_y()
        + barra.get_height() / 2,

        f"{valor:.1f}%",

        va="center",
        fontsize=TAMANHO_ROTULO
    )


adicionar_titulo(
    ax,
    "Onde estão surgindo novos estabelecimentos de Food Service?",
    "Percentual dos estabelecimentos ativos que iniciaram atividade entre 2023 e setembro de 2026"
)


ax.set_xlabel(
    "Estabelecimentos iniciados desde 2023 (%)"
)


ax.set_xlim(
    0,
    max(
        top15_recencia["taxa_recencia"]
    ) * 1.12
)


ax.invert_yaxis()


ax.spines[
    ["top", "right", "left"]
].set_visible(False)


ax.grid(
    axis="x",
    alpha=0.2
)


ax.set_axisbelow(True)


plt.tight_layout(
    rect=[0, 0, 1, 0.94]
)


plt.savefig(
    PASTA_GRAFICOS / "02_escala_dinamica.png",
    bbox_inches="tight"
)


plt.close()


# ============================================================
# 3. PERFIL DOS SEGMENTOS
# ============================================================

print("\n[3/5] Gerando perfil dos segmentos...")

segmentos = [
    "Alimentação preparada",
    "Lanchonetes",
    "Restaurantes",
    "Outros Food Service",
    "Padarias e confeitaria",
    "Catering empresarial",
    "Eventos e buffet",
    "Cantinas"
]


top10 = (
    df
    .nlargest(
        10,
        "estabelecimentos_food_service"
    )
    .copy()
)


for segmento in segmentos:

    top10[
        f"{segmento}_pct"
    ] = (
        top10[segmento]
        / top10["estabelecimentos_food_service"]
        * 100
    )


fig, ax = plt.subplots(
    figsize=(13, 9)
)


base = np.zeros(
    len(top10)
)


for segmento in segmentos:

    valores = top10[
        f"{segmento}_pct"
    ]

    ax.barh(
        top10["municipio_label"],
        valores,
        left=base,
        label=segmento
    )

    base += valores.values


adicionar_titulo(
    ax,
    "Como o perfil do Food Service varia entre os grandes mercados?",
    "Participação dos principais segmentos na base ativa de cada município"
)


ax.set_xlabel(
    "Participação dos estabelecimentos (%)"
)


ax.set_xlim(
    0,
    100
)


ax.invert_yaxis()


ax.legend(
    bbox_to_anchor=(1.02, 1),
    loc="upper left",
    frameon=False
)


ax.spines[
    ["top", "right", "left"]
].set_visible(False)


ax.grid(
    axis="x",
    alpha=0.2
)


ax.set_axisbelow(True)


plt.tight_layout(
    rect=[0, 0, 0.82, 0.94]
)


plt.savefig(
    PASTA_GRAFICOS / "03_perfil_segmentos.png",
    bbox_inches="tight"
)


plt.close()


# ============================================================
# 4. MERCADOS EMERGENTES
# ============================================================

print("\n[4/5] Gerando mercados emergentes...")


emergentes = df[
    (
        df["estabelecimentos_food_service"] >= 100
    )
    &
    (
        df["estabelecimentos_food_service"] <= 499
    )
].copy()


# ------------------------------------------------------------
# Seleciona os 12 mercados com maior número absoluto
# de estabelecimentos iniciados desde 2023
# ------------------------------------------------------------

emergentes = (
    emergentes
    .nlargest(
        12,
        "estabelecimentos_recentes"
    )
    .copy()
)


emergentes["estabelecimentos_anteriores"] = (
    emergentes["estabelecimentos_food_service"]
    - emergentes["estabelecimentos_recentes"]
)


# ------------------------------------------------------------
# NOVO AJUSTE:
# Ordena visualmente pelo percentual mostrado
# à direita, do maior para o menor
# ------------------------------------------------------------

emergentes = (
    emergentes
    .sort_values(
        "taxa_recencia",
        ascending=False
    )
    .copy()
)


fig, ax = plt.subplots(
    figsize=(13, 9)
)


ax.barh(
    emergentes["municipio_label"],
    emergentes["estabelecimentos_anteriores"],
    label="Iniciados antes de 2023"
)


ax.barh(
    emergentes["municipio_label"],
    emergentes["estabelecimentos_recentes"],
    left=emergentes["estabelecimentos_anteriores"],
    label="Iniciados desde 2023"
)


# ------------------------------------------------------------
# Percentual no final da barra
# ------------------------------------------------------------

for indice, (_, linha) in enumerate(
    emergentes.iterrows()
):

    ax.text(
        linha["estabelecimentos_food_service"] + 4,
        indice,
        f"{linha['taxa_recencia']:.1f}%",
        va="center",
        fontsize=TAMANHO_ROTULO
    )


adicionar_titulo(
    ax,
    "Mercados emergentes: escala e expansão recente",
    "Municípios com 100–499 operadores ativos e maior número absoluto de estabelecimentos iniciados desde 2023"
)


ax.set_xlabel(
    "Estabelecimentos Food Service ativos"
)


ax.invert_yaxis()


ax.legend(
    loc="upper center",
    bbox_to_anchor=(0.5, -0.10),
    ncol=2,
    frameon=False
)


ax.spines[
    ["top", "right", "left"]
].set_visible(False)


ax.grid(
    axis="x",
    alpha=0.2
)


ax.set_axisbelow(True)


plt.tight_layout(
    rect=[0, 0, 1, 0.94],
    pad=2.0
)


plt.savefig(
    PASTA_GRAFICOS
    / "04_mercados_emergentes.png",
    bbox_inches="tight"
)


plt.close()


# ============================================================
# 5. ESTRUTURA EMPRESARIAL DOS MERCADOS EMERGENTES
# ============================================================

print(
    "\n[5/5] Gerando estrutura empresarial "
    "dos mercados emergentes..."
)


# ------------------------------------------------------------
# Usar exatamente os mesmos mercados do gráfico 4
# ------------------------------------------------------------

estrutura = emergentes.copy()


# ------------------------------------------------------------
# Estabelecimentos pertencentes a empresas que não são
# microempresas
# ------------------------------------------------------------

estrutura["estabelecimentos_nao_micro"] = (
    estrutura["Empresa de Pequeno Porte"]
    + estrutura["Demais"]
)


# ------------------------------------------------------------
# Percentual
# ------------------------------------------------------------

estrutura["percentual_nao_micro"] = (
    estrutura["estabelecimentos_nao_micro"]
    / estrutura["estabelecimentos_food_service"]
    * 100
)


# Maior percentual primeiro

estrutura = (
    estrutura
    .sort_values(
        "percentual_nao_micro",
        ascending=False
    )
    .copy()
)


# ------------------------------------------------------------
# Gráfico
# ------------------------------------------------------------

fig, ax = plt.subplots(
    figsize=(13, 9)
)


barras = ax.barh(
    estrutura["municipio_label"],
    estrutura["percentual_nao_micro"]
)


# ------------------------------------------------------------
# Rótulos
# ------------------------------------------------------------

for barra, (_, linha) in zip(
    barras,
    estrutura.iterrows()
):

    percentual = linha[
        "percentual_nao_micro"
    ]

    quantidade = linha[
        "estabelecimentos_nao_micro"
    ]

    total = linha[
        "estabelecimentos_food_service"
    ]

    ax.text(
        barra.get_width() + 0.25,

        barra.get_y()
        + barra.get_height() / 2,

        (
            f"{percentual:.1f}%  "
            f"({quantidade:,.0f} de {total:,.0f})"
        ).replace(",", "."),

        va="center",
        fontsize=TAMANHO_ROTULO
    )


# ------------------------------------------------------------
# Título
# ------------------------------------------------------------

adicionar_titulo(
    ax,
    "Os mercados emergentes são formados apenas por microempresas?",
    "Percentual dos estabelecimentos pertencentes a empresas que não são microempresas"
)


ax.set_xlabel(
    "Estabelecimentos pertencentes a empresas que não são microempresas (%)"
)


ax.set_xlim(
    0,
    max(
        estrutura["percentual_nao_micro"]
    ) * 1.28
)


ax.invert_yaxis()


ax.spines[
    ["top", "right", "left"]
].set_visible(False)


ax.grid(
    axis="x",
    alpha=0.2
)


ax.set_axisbelow(True)


plt.tight_layout(
    rect=[0, 0, 1, 0.94]
)


plt.savefig(
    PASTA_GRAFICOS
    / "05_estrutura_mercados_emergentes.png",
    bbox_inches="tight"
)


plt.close()


# ============================================================
# FINAL
# ============================================================

print("\n" + "=" * 70)
print("GRÁFICOS GERADOS")
print("=" * 70)


arquivos = [
    "01_top_mercados_escala.png",
    "02_escala_dinamica.png",
    "03_perfil_segmentos.png",
    "04_mercados_emergentes.png",
    "05_estrutura_mercados_emergentes.png"
]


for arquivo in arquivos:

    print(
        f"✓ outputs/graficos/{arquivo}"
    )


print("\nConcluído.")
print("=" * 70)