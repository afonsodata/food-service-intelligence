import pandas as pd
from pathlib import Path


# ============================================================
# CONFIGURAÇÃO
# ============================================================

PASTA_PROJETO = Path(__file__).resolve().parent

ARQUIVO_FOOD_SERVICE = (
    PASTA_PROJETO / "food_service_analitico_porte.csv"
)

ARQUIVO_POPULACAO = (
    PASTA_PROJETO / "estimativa_dou_2026.xlsx"
)

ARQUIVO_TOM_IBGE = (
    PASTA_PROJETO / "municipios_tom_ibge.csv"
)

PASTA_OUTPUT = (
    PASTA_PROJETO / "outputs"
)

PASTA_OUTPUT.mkdir(
    exist_ok=True
)


# ============================================================
# CONFIGURAÇÕES DA ANÁLISE
# ============================================================

ANO_INICIO_RECENCIA = 2023

SEGMENTOS = [
    "Alimentação preparada",
    "Cantinas",
    "Catering empresarial",
    "Eventos e buffet",
    "Lanchonetes",
    "Outros Food Service",
    "Padarias e confeitaria",
    "Restaurantes",
]

PORTES = [
    "Microempresa",
    "Empresa de Pequeno Porte",
    "Demais",
    "Não informado",
    "Não encontrado",
]


# ============================================================
# 1. CARREGAR BASES
# ============================================================

print("=" * 70)
print("ANÁLISE DE MERCADO — FOOD SERVICE")
print("=" * 70)

print("\n[1/7] Carregando bases...")

df_food = pd.read_csv(
    ARQUIVO_FOOD_SERVICE,
    sep=";",
    encoding="utf-8-sig",
    dtype=str,
)

df_pop = pd.read_excel(
    ARQUIVO_POPULACAO,
    sheet_name="municípios",
    header=None,
)

df_tom = pd.read_csv(
    ARQUIVO_TOM_IBGE,
    encoding="latin1",
    sep=";",
)

print(
    f"Base Food Service: {df_food.shape}"
)

print(
    f"Base população: {df_pop.shape}"
)

print(
    f"Base TOM/IBGE: {df_tom.shape}"
)


# ============================================================
# 2. PREPARAR POPULAÇÃO
# ============================================================

print("\n[2/7] Preparando população...")

df_pop = df_pop.iloc[2:].copy()

df_pop.columns = [
    "uf",
    "codigo_uf",
    "codigo_municipio",
    "municipio",
    "populacao",
]

df_pop["codigo_municipio"] = pd.to_numeric(
    df_pop["codigo_municipio"],
    errors="coerce",
)

df_pop["populacao"] = pd.to_numeric(
    df_pop["populacao"],
    errors="coerce",
)

df_pop["uf"] = (
    df_pop["uf"]
    .astype(str)
    .str.strip()
)

df_pop = df_pop[
    [
        "uf",
        "codigo_municipio",
        "municipio",
        "populacao",
    ]
].copy()

print(
    f"Municípios com população: "
    f"{len(df_pop):,}"
)


# ============================================================
# 3. PADRONIZAR FOOD SERVICE
# ============================================================

print("\n[3/7] Padronizando base Food Service...")

df_food["codigo_municipio"] = pd.to_numeric(
    df_food["codigo_municipio"],
    errors="coerce",
)

df_food["uf"] = (
    df_food["uf"]
    .astype(str)
    .str.strip()
)

df_food["municipio"] = (
    df_food["municipio"]
    .astype(str)
    .str.strip()
)

df_food["porte_empresa"] = (
    df_food["porte_empresa"]
    .fillna("Não encontrado")
    .astype(str)
    .str.strip()
)

df_food["data_inicio_atividade"] = (
    df_food["data_inicio_atividade"]
    .astype(str)
    .str.strip()
)

df_food["data_abertura"] = pd.to_datetime(
    df_food["data_inicio_atividade"],
    format="%Y%m%d",
    errors="coerce",
)

df_food["ano_abertura"] = (
    df_food["data_abertura"]
    .dt.year
)

df_food["abertura_recente"] = (
    df_food["ano_abertura"]
    >= ANO_INICIO_RECENCIA
)


# ============================================================
# 4. MERCADO POR MUNICÍPIO
# ============================================================

print("\n[4/7] Construindo mercado municipal...")

food_municipios = (
    df_food
    .groupby(
        [
            "uf",
            "codigo_municipio",
        ],
        as_index=False,
    )
    .size()
    .rename(
        columns={
            "size": "estabelecimentos_food_service"
        }
    )
)

nomes_municipios = (
    df_food[
        [
            "uf",
            "codigo_municipio",
            "municipio",
        ]
    ]
    .drop_duplicates(
        subset=[
            "uf",
            "codigo_municipio",
        ]
    )
)

food_municipios = food_municipios.merge(
    nomes_municipios,
    on=[
        "uf",
        "codigo_municipio",
    ],
    how="left",
)


# ============================================================
# 5. INTEGRAR IBGE E POPULAÇÃO
# ============================================================

print("\n[5/7] Integrando códigos IBGE e população...")

df_tom = df_tom[
    [
        "CÓDIGO DO MUNICÍPIO - TOM",
        "CÓDIGO DO MUNICÍPIO - IBGE",
        "UF",
    ]
].copy()

df_tom[
    "CÓDIGO DO MUNICÍPIO - TOM"
] = pd.to_numeric(
    df_tom[
        "CÓDIGO DO MUNICÍPIO - TOM"
    ],
    errors="coerce",
)

df_tom[
    "CÓDIGO DO MUNICÍPIO - IBGE"
] = pd.to_numeric(
    df_tom[
        "CÓDIGO DO MUNICÍPIO - IBGE"
    ],
    errors="coerce",
)

df_tom["UF"] = (
    df_tom["UF"]
    .astype(str)
    .str.strip()
)

# O código municipal utilizado pela base de população
# corresponde aos últimos 5 dígitos do código IBGE.
df_tom["codigo_municipio_pop"] = (
    df_tom["CÓDIGO DO MUNICÍPIO - IBGE"]
    % 100000
)

df_tom = df_tom.rename(
    columns={
        "CÓDIGO DO MUNICÍPIO - TOM":
            "codigo_municipio"
    }
)

df_mercado = food_municipios.merge(
    df_tom[
        [
            "UF",
            "codigo_municipio",
            "CÓDIGO DO MUNICÍPIO - IBGE",
            "codigo_municipio_pop",
        ]
    ],
    left_on=[
        "uf",
        "codigo_municipio",
    ],
    right_on=[
        "UF",
        "codigo_municipio",
    ],
    how="left",
)

df_mercado = df_mercado.drop(
    columns=["UF"]
)

df_pop_chave = df_pop[
    [
        "uf",
        "codigo_municipio",
        "populacao",
    ]
].copy()

df_pop_chave = df_pop_chave.rename(
    columns={
        "codigo_municipio":
            "codigo_municipio_pop"
    }
)

df_mercado = df_mercado.merge(
    df_pop_chave,
    on=[
        "uf",
        "codigo_municipio_pop",
    ],
    how="left",
)

df_mercado["food_service_por_100mil"] = (
    df_mercado[
        "estabelecimentos_food_service"
    ]
    / df_mercado["populacao"]
    * 100000
)

print(
    f"Municípios com Food Service: "
    f"{len(df_mercado):,}"
)

print(
    f"Municípios sem população: "
    f"{df_mercado['populacao'].isna().sum():,}"
)


# ============================================================
# 6. PERFIL, RECÊNCIA E PORTE
# ============================================================

print(
    "\n[6/7] Calculando perfil, dinâmica "
    "e estrutura empresarial..."
)


# ------------------------------------------------------------
# Perfil por segmento
# ------------------------------------------------------------

df_perfil = (
    df_food
    .groupby(
        [
            "uf",
            "codigo_municipio",
            "segmento_food_service",
        ]
    )
    .size()
    .unstack(fill_value=0)
    .reset_index()
)

for segmento in SEGMENTOS:

    if segmento not in df_perfil.columns:
        df_perfil[segmento] = 0

df_analise = df_mercado.merge(
    df_perfil[
        [
            "uf",
            "codigo_municipio",
        ] + SEGMENTOS
    ],
    on=[
        "uf",
        "codigo_municipio",
    ],
    how="left",
)


# ------------------------------------------------------------
# Recência
# ------------------------------------------------------------

df_recencia = (
    df_food
    .groupby(
        [
            "uf",
            "codigo_municipio",
        ]
    )
    .agg(
        estabelecimentos_recentes=(
            "abertura_recente",
            "sum",
        ),
        estabelecimentos_total=(
            "cnpj",
            "count",
        ),
    )
    .reset_index()
)

df_recencia["taxa_recencia"] = (
    df_recencia[
        "estabelecimentos_recentes"
    ]
    / df_recencia["estabelecimentos_total"]
    * 100
)

df_analise = df_analise.merge(
    df_recencia,
    on=[
        "uf",
        "codigo_municipio",
    ],
    how="left",
)


# ------------------------------------------------------------
# Porte empresarial
# ------------------------------------------------------------

df_porte = (
    df_food
    .groupby(
        [
            "uf",
            "codigo_municipio",
            "porte_empresa",
        ]
    )
    .size()
    .unstack(fill_value=0)
    .reset_index()
)

for porte in PORTES:

    if porte not in df_porte.columns:
        df_porte[porte] = 0

df_porte = df_porte[
    [
        "uf",
        "codigo_municipio",
    ] + PORTES
]

df_analise = df_analise.merge(
    df_porte,
    on=[
        "uf",
        "codigo_municipio",
    ],
    how="left",
)


# ------------------------------------------------------------
# Indicadores de estrutura empresarial
# ------------------------------------------------------------

df_analise["porte_maior"] = (
    df_analise["Empresa de Pequeno Porte"]
    + df_analise["Demais"]
)

df_analise["taxa_porte_maior"] = (
    df_analise["porte_maior"]
    / df_analise["estabelecimentos_food_service"]
    * 100
)

df_analise["porte_dominante"] = (
    df_analise[
        [
            "Microempresa",
            "Empresa de Pequeno Porte",
            "Demais",
        ]
    ]
    .idxmax(axis=1)
)


# ------------------------------------------------------------
# Segmento dominante
# ------------------------------------------------------------

df_analise["segmento_dominante"] = (
    df_analise[SEGMENTOS]
    .idxmax(axis=1)
)

df_analise["total_segmentos"] = (
    df_analise[SEGMENTOS]
    .sum(axis=1)
)


# ============================================================
# 7. ORGANIZAÇÃO E EXPORTAÇÃO
# ============================================================

print("\n[7/7] Organizando resultado final...")


colunas_principais = [
    "uf",
    "codigo_municipio",
    "municipio",
    "CÓDIGO DO MUNICÍPIO - IBGE",
    "populacao",
    "estabelecimentos_food_service",
    "food_service_por_100mil",
    "estabelecimentos_recentes",
    "taxa_recencia",
    "porte_dominante",
    "porte_maior",
    "taxa_porte_maior",
    "Microempresa",
    "Empresa de Pequeno Porte",
    "Demais",
    "Não informado",
    "Não encontrado",
    "segmento_dominante",
    "total_segmentos",
]


colunas_finais = (
    colunas_principais
    + SEGMENTOS
)


colunas_finais = [
    coluna
    for coluna in colunas_finais
    if coluna in df_analise.columns
]


df_analise = (
    df_analise[
        colunas_finais
    ]
    .sort_values(
        "estabelecimentos_food_service",
        ascending=False,
    )
)


arquivo_saida = (
    PASTA_OUTPUT
    / "mercado_analise.csv"
)

df_analise.to_csv(
    arquivo_saida,
    index=False,
    encoding="utf-8-sig",
)


# ============================================================
# RESUMO FINAL
# ============================================================

print("\n" + "=" * 70)
print("ANÁLISE CONCLUÍDA")
print("=" * 70)

print(
    f"\nMunicípios analisados: "
    f"{len(df_analise):,}"
)

print(
    f"Estabelecimentos Food Service: "
    f"{df_analise['estabelecimentos_food_service'].sum():,}"
)

print(
    "\nDistribuição dos estabelecimentos por porte:"
)

total_estabelecimentos = (
    df_analise[
        [
            "Microempresa",
            "Empresa de Pequeno Porte",
            "Demais",
        ]
    ]
    .sum()
    .sum()
)

for porte in [
    "Microempresa",
    "Empresa de Pequeno Porte",
    "Demais",
]:

    quantidade = df_analise[porte].sum()

    percentual = (
        quantidade
        / total_estabelecimentos
        * 100
    )

    print(
        f"  {porte:<25}"
        f"{quantidade:>10,.0f}"
        f"  ({percentual:>6.2f}%)"
    )


print(
    f"\nArquivo salvo em:"
    f"\n{arquivo_saida}"
)

print("=" * 70)