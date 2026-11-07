
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from paginas.dados import formatar

from paginas.componentes import (
    pesquisar,
    mostrar_ranking,
    mostrar_dispersao
)


def preparar_comparacao(base, caracteristica):
    colunas = {
        "Raridade": "raridade_label",
        "Elemento": "elemento",
        "Região": "regiao",
        "Modelo corporal": "modelo_3d",
        "Função no time": "funcao",
        "Arconte": "arconte_label"
    }

    coluna = colunas[caracteristica]

    dados = base.copy()

    if coluna == "funcao":
        dados = dados.explode(
            "funcoes_lista"
        )

        dados["funcao"] = (
            dados["funcoes_lista"]
        )

    dados = dados.dropna(
        subset=[coluna]
    )

    return dados, coluna


def renderizar(
    base,
    busca,
    cores
):
    st.header(
        "Análise 3 — Interesse e características "
        "dos personagens"
    )

    st.write(
        "Investigamos associações entre características "
        "dos personagens, interesse registrado em pulls "
        "e frequência histórica de retorno."
    )

    a, b, c = st.columns(3)

    a.metric(
        "Personagens nos filtros",
        len(base)
    )

    b.metric(
        "Pulls acumulados",
        formatar(
            base["total_pulls"].sum()
        )
    )

    c.metric(
        "Elegíveis pelo critério",
        int(
            base["elegivel_64"].sum()
        )
    )

    st.caption(
        "Os pulls são acumulados por personagem, "
        "não separados por banner ou ano. "
        "As comparações não representam causalidade."
    )

    # ========================================================
    # GRÁFICO 1 — TOTAL DE PULLS
    # ========================================================

    st.subheader(
        "1. Ranking — Total de pulls"
    )

    mostrar_ranking(
        dados=pesquisar(base, busca),
        metrica="total_pulls",
        eixo="Total de pulls acumulados",
        chave="ordem_a3_pulls",
        cores=cores
    )

    # ========================================================
    # GRÁFICO 2 — PULLS X CÓPIAS
    # ========================================================

    st.subheader(
        "2. Total de pulls × média de cópias"
    )

    st.write(
        "Comparamos o volume acumulado de pulls "
        "com a média de cópias por jogador."
    )

    mostrar_dispersao(
        dados=base,
        x="total_pulls",
        y="media_copias_jogador",
        eixo_x="Total de pulls acumulados",
        eixo_y="Média de cópias por jogador",
        busca=busca,
        cores=cores
    )

    # ========================================================
    # CONTROLES DAS COMPARAÇÕES
    # ========================================================

    st.divider()

    st.markdown(
        "### Comparação por características"
    )

    caracteristica = st.selectbox(
        "Comparar personagens por",
        [
            "Raridade",
            "Elemento",
            "Região",
            "Modelo corporal",
            "Função no time",
            "Arconte"
        ],
        key="caracteristica_a3"
    )

    comparacao, coluna = preparar_comparacao(
        base,
        caracteristica
    )

    # ========================================================
    # GRÁFICO 3 — MÉDIA OU MEDIANA DE PULLS
    # ========================================================

    st.subheader(
        "3. Pulls por característica"
    )

    medida = st.radio(
        "Medida de interesse",
        [
            "Média",
            "Mediana"
        ],
        horizontal=True,
        key="medida_pulls_a3"
    )

    dados_pulls = comparacao.dropna(
        subset=["total_pulls"]
    )

    if dados_pulls.empty:
        st.info(
            "Sem dados para essa comparação."
        )

    else:
        resumo = (
            dados_pulls.groupby(coluna)
            .agg(
                media_pulls=(
                    "total_pulls",
                    "mean"
                ),
                mediana_pulls=(
                    "total_pulls",
                    "median"
                ),
                quantidade=(
                    "personagem",
                    "nunique"
                )
            )
            .reset_index()
        )

        metrica = (
            "media_pulls"
            if medida == "Média"
            else "mediana_pulls"
        )

        resumo = resumo.sort_values(
            metrica,
            ascending=False
        )

        fig = px.bar(
            resumo,
            x=metrica,
            y=coluna,
            orientation="h",
            color=coluna,
            text=metrica,
            hover_data=["quantidade"],
            labels={
                metrica: (
                    f"{medida} de pulls"
                ),
                coluna: caracteristica,
                "quantidade": (
                    "Número de personagens"
                )
            }
        )

        fig.update_traces(
            texttemplate="%{text:,.0f}",
            textposition="outside",
            cliponaxis=False
        )

        fig.update_layout(
            height=max(
                440,
                len(resumo) * 48 + 140
            ),
            showlegend=False,
            yaxis={
                "categoryorder": "total ascending"
            },
            margin={"r": 90}
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.caption(
            "A quantidade de personagens por grupo "
            "aparece ao passar o mouse sobre as barras."
        )


    # ========================================================
    # GRÁFICO 4 — FREQUÊNCIA DE RETORNO
    # ========================================================

    st.subheader(
        "4. Frequência histórica de retorno "
        "por característica"
    )

    st.write(
        "Comparamos os intervalos históricos "
        "individuais entre banners. Valores menores "
        "representam retornos mais frequentes."
    )

    dados_retorno = comparacao.dropna(
        subset=["intervalo_medio"]
    )

    if dados_retorno.empty:
        st.info(
            "Não há intervalos históricos suficientes."
        )

    else:
        resumo = (
            dados_retorno.groupby(coluna)
            .agg(
                media_intervalo=(
                    "intervalo_medio",
                    "mean"
                ),
                mediana_intervalo=(
                    "intervalo_medio",
                    "median"
                ),
                quantidade=(
                    "personagem",
                    "nunique"
                )
            )
            .reset_index()
        )

        medida_retorno = st.radio(
            "Medida dos intervalos",
            [
                "Média",
                "Mediana"
            ],
            horizontal=True,
            key="medida_retorno_a3"
        )

        metrica = (
            "media_intervalo"
            if medida_retorno == "Média"
            else "mediana_intervalo"
        )

        resumo = resumo.sort_values(
            metrica,
            ascending=False
        )

        fig = px.bar(
            resumo,
            x=metrica,
            y=coluna,
            orientation="h",
            color=coluna,
            text=metrica,
            hover_data=["quantidade"],
            labels={
                metrica: (
                    f"{medida_retorno} do intervalo "
                    "histórico (dias)"
                ),
                coluna: caracteristica,
                "quantidade": (
                    "Número de personagens"
                )
            }
        )

        fig.update_traces(
            texttemplate="%{text:.1f}",
            textposition="outside",
            cliponaxis=False
        )

        fig.update_layout(
            height=max(
                440,
                len(resumo) * 48 + 140
            ),
            showlegend=False,
            yaxis={
                "categoryorder": "total ascending"
            },
            margin={"r": 90}
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.caption(
            "Cada personagem contribui com seu "
            "intervalo médio individual. Personagens "
            "sem intervalos históricos são excluídos "
            "desta comparação."
        )