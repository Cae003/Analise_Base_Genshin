
from pathlib import Path

import pandas as pd
import streamlit as st

from paginas.dados import carregar_base
from paginas import inicio, analise1, analise2, analise3


# ============================================================
# CONFIGURAÇÕES GERAIS
# ============================================================

st.set_page_config(
    page_title="Genshin Impact | Estudo de banners",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

PASTA_PROJETO = Path(__file__).resolve().parent

# ALTERE A ORIGEM DO CSV AQUI.
#
# Arquivo local:
CSV_ORIGEM = PASTA_PROJETO / "arquivo.csv"
#
# Ou URL direta para um CSV:
# CSV_ORIGEM = "https://exemplo.com/arquivo.csv"

DATA_CORTE = pd.Timestamp("2026-02-24")

VERSAO_ALVO = "Luna V"  # Versão 6.4
DISTANCIA_MINIMA = 2

CORES_RARIDADE = {
    "4 estrelas": "#9B59B6",
    "5 estrelas": "#D4A72C"
}

PAGINAS = [
    "Início · Base de dados",
    "Análise 1 · Ausência e cronologia",
    "Análise 2 · Frequência e retorno",
    "Análise 3 · Interesse e características"
]


# ============================================================
# ESTILO
# ============================================================

st.markdown(
    """
    <style>
    .st-key-cabecalho_fixo {
        position: sticky;
        top: 2.75rem;
        z-index: 999;
        background: var(--background-color);
        padding: 0.65rem 0 0.5rem 0;
        border-bottom: 1px solid rgba(140,140,140,0.25);
    }

    .st-key-cabecalho_fixo p {
        margin-bottom: 0;
    }

    div[data-testid="stMetric"] {
        border: 1px solid rgba(140,140,140,0.18);
        border-radius: 10px;
        padding: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# CARREGAMENTO DA BASE
# ============================================================

try:
    if isinstance(CSV_ORIGEM, Path):
        if not CSV_ORIGEM.exists():
            st.error(
                f"Arquivo CSV não encontrado: {CSV_ORIGEM}"
            )
            st.stop()

        # A versão muda quando o arquivo local é atualizado.
        versao_cache = CSV_ORIGEM.stat().st_mtime_ns
        origem = str(CSV_ORIGEM)
    else:
        versao_cache = str(CSV_ORIGEM)
        origem = str(CSV_ORIGEM)

    original, df, aparicoes, intervalos = carregar_base(
        origem=origem,
        versao_cache=versao_cache,
        data_corte=DATA_CORTE,
        versao_alvo=VERSAO_ALVO,
        distancia_minima=DISTANCIA_MINIMA
    )

except Exception as erro:
    st.error(f"Erro ao carregar a base: {erro}")
    st.stop()


# ============================================================
# NAVEGAÇÃO FIXA
# ============================================================

with st.container(key="cabecalho_fixo"):
    st.markdown(
        "**✦ Genshin Impact — Estudo histórico de banners**"
    )

    pagina = st.segmented_control(
        "Navegação",
        options=PAGINAS,
        default=PAGINAS[0],
        label_visibility="collapsed",
        key="pagina_atual"
    )


# ============================================================
# FILTROS
# ============================================================

with st.sidebar:
    st.header("Filtros")

    busca = st.text_input(
        "Pesquisar personagem",
        placeholder="Digite um nome..."
    )

    st.divider()

    filtro_elegibilidade = st.radio(
        "Elegibilidade para a 6.4",
        [
            "Somente elegíveis",
            "Somente excluídos"
        ],
        index=0,
        help=(
            "Personagens 5★ precisam ter uma distância "
            "mínima de duas versões desde sua última "
            "aparição registrada. Personagens 4★ não "
            "têm essa restrição. É uma hipótese de "
            "seleção para o estudo, não uma regra "
            "oficial garantida."
        )
    )

    st.divider()
    st.markdown("**Raridade**")

    mostrar_4 = st.checkbox(
        "4 estrelas",
        value=True
    )

    mostrar_5 = st.checkbox(
        "5 estrelas",
        value=True
    )

    incluir_padrao = st.checkbox(
        "Incluir 5★ do banner padrão",
        value=False
    )

    filtro_arconte = st.selectbox(
        "Arcontes (5★)",
        [
            "Todos",
            "Somente Arcontes",
            "Excluir Arcontes"
        ]
    )

    st.divider()

    regioes = st.multiselect(
        "Região",
        sorted(
            df["regiao"].dropna().astype(str).unique()
        )
    )

    elementos = st.multiselect(
        "Elemento",
        sorted(
            df["elemento"].dropna().astype(str).unique()
        )
    )

    modelos = st.multiselect(
        "Modelo corporal",
        sorted(
            df["modelo_3d"].dropna().astype(str).unique()
        )
    )

    todas_funcoes = sorted({
        funcao
        for lista in df["funcoes_lista"]
        for funcao in lista
    })

    funcoes = st.multiselect(
        "Função no time",
        todas_funcoes,
        help=(
            "Personagens podem exercer várias funções. "
            "Ao selecionar mais de uma, serão incluídos "
            "aqueles que possuem pelo menos uma delas."
        )
    )


# ============================================================
# APLICAR FILTROS
# ============================================================

raridades = []

if mostrar_4:
    raridades.append(4)

if mostrar_5:
    raridades.append(5)

base = df[
    df["raridade"].isin(raridades)
].copy()

if not incluir_padrao:
    base = base[
        ~(
            (base["raridade"] == 5)
            & base["is_banner_padrao"]
        )
    ]

if filtro_arconte == "Somente Arcontes":
    base = base[
        (base["raridade"] == 4)
        | base["is_arconte"]
    ]

elif filtro_arconte == "Excluir Arcontes":
    base = base[
        (base["raridade"] == 4)
        | ~base["is_arconte"]
    ]

if regioes:
    base = base[
        base["regiao"].isin(regioes)
    ]

if elementos:
    base = base[
        base["elemento"].isin(elementos)
    ]

if modelos:
    base = base[
        base["modelo_3d"].isin(modelos)
    ]

if funcoes:
    funcoes_set = set(funcoes)

    base = base[
        base["funcoes_lista"].apply(
            lambda lista: bool(
                set(lista) & funcoes_set
            )
        )
    ]

if filtro_elegibilidade == "Somente elegíveis":
    base = base[
        base["elegivel_64"]
    ]

elif filtro_elegibilidade == "Somente excluídos":
    base = base[
        base["status_elegibilidade"]
        == "Excluído pelo critério"
    ]

nomes = set(base["personagem"])

aparicoes_filtradas = aparicoes[
    aparicoes["personagem"].isin(nomes)
].copy()

intervalos_filtrados = intervalos[
    intervalos["personagem"].isin(nomes)
].copy()


# ============================================================
# EXECUTAR A PÁGINA ESCOLHIDA
# ============================================================

if pagina == PAGINAS[0]:
    inicio.renderizar(
        original=original,
        base_completa=df,
        data_corte=DATA_CORTE
    )

elif pagina == PAGINAS[1]:
    analise1.renderizar(
        base=base,
        aparicoes=aparicoes_filtradas,
        todas_aparicoes=aparicoes,
        intervalos=intervalos_filtrados,
        busca=busca,
        cores=CORES_RARIDADE
    )

elif pagina == PAGINAS[2]:
    analise2.renderizar(
        base=base,
        busca=busca,
        cores=CORES_RARIDADE
    )

elif pagina == PAGINAS[3]:
    analise3.renderizar(
        base=base,
        busca=busca,
        cores=CORES_RARIDADE
    )
