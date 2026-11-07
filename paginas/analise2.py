
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from paginas.componentes import (
    HOVER,
    HOVER_COLS,
    pesquisar,
    mostrar_ranking
)


def renderizar(
    base,
    busca,
    cores
):
    st.header(
        "Análise 2 — Frequência e padrões de retorno"
    )

    st.write(
        "Analisamos a frequência de aparições "
        "e comparamos a ausência atual com o "
        "intervalo histórico individual."
    )

    validos = base[
        (base["intervalo_medio"] > 0)
        & base["ausencia_atual"].notna()
    ].copy()

    a, b, c = st.columns(3)

    a.metric(
        "Personagens nos filtros",
        len(base)
    )

    b.metric(
        "Com intervalos históricos",
        len(validos)
    )

    c.metric(
        "Acima da média individual",
        int(
            (
                validos["ausencia_atual"]
                > validos["intervalo_medio"]
            ).sum()
        )
    )

    # ========================================================
    # GRÁFICO 1 — QUANTIDADE DE BANNERS
    # ========================================================

    st.subheader(
        "1. Quantidade de banners por personagem"
    )

    mostrar_ranking(
        dados=pesquisar(base, busca),
        metrica="qtd_banners",
        eixo="Quantidade de banners",
        chave="ordem_a2_banners",
        cores=cores
    )

    # ========================================================
    # GRÁFICO 2 — AUSÊNCIA X INTERVALO MÉDIO
    # ========================================================

    st.subheader(
        "2. Ausência atual × intervalo médio individual"
    )

    st.write(
        "A diagonal representa igualdade entre "
        "ausência atual e intervalo médio histórico. "
        "Pontos acima da linha estão há mais tempo "
        "sem banner do que sua média individual."
    )

    if validos.empty:
        st.info(
            "Não há personagens com histórico suficiente."
        )

    else:
        fig = px.scatter(
            validos,
            x="intervalo_medio",
            y="ausencia_atual",
            color="raridade_label",
            color_discrete_map=cores,
            custom_data=HOVER_COLS,
            labels={
                "intervalo_medio": (
                    "Intervalo médio histórico (dias)"
                ),
                "ausencia_atual": (
                    "Ausência atual (dias)"
                ),
                "raridade_label": "Raridade"
            }
        )

        fig.update_traces(
            marker={
                "size": 10,
                "opacity": (
                    0.25 if busca.strip() else 0.8
                )
            },
            hovertemplate=HOVER
        )

        fig.add_trace(
            go.Scatter(
                x=[0, 600],
                y=[0, 600],
                mode="lines",
                name="Ausência = média",
                line={
                    "color": "#888888",
                    "dash": "dash",
                    "width": 2
                },
                hoverinfo="skip"
            )
        )

        if busca.strip():
            destaque = pesquisar(
                validos,
                busca
            )

            if not destaque.empty:
                fig.add_trace(
                    go.Scatter(
                        x=destaque["intervalo_medio"],
                        y=destaque["ausencia_atual"],
                        mode="markers+text",
                        text=destaque["personagem"],
                        textposition="top center",
                        name="Personagem pesquisado",
                        marker={
                            "size": 18,
                            "symbol": "diamond",
                            "color": [
                                cores.get(
                                    raridade,
                                    "#888888"
                                )
                                for raridade in destaque[
                                    "raridade_label"
                                ]
                            ]
                        },
                        customdata=destaque[
                            HOVER_COLS
                        ].astype(str).to_numpy(),
                        hovertemplate=HOVER
                    )
                )

        max_y = max(
            600,
            float(
                validos["ausencia_atual"].max()
            ) * 1.1
        )

        fig.update_layout(
            height=650,
            xaxis={
                "range": [0, 600],
                "title": (
                    "Intervalo médio histórico (dias)"
                )
            },
            yaxis={
                "range": [0, max_y],
                "title": "Ausência atual (dias)"
            },
            legend_title="Raridade"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.caption(
            "O eixo X permanece fixo de 0 a 600 dias. "
            "Personagens acima desse limite não aparecem "
            "na área visível, mas continuam nos cálculos."
        )

    # ========================================================
    # GRÁFICO 3 — ÍNDICE DE AUSÊNCIA
    # ========================================================

    st.subheader(
        "3. Índice de ausência relativa"
    )

    st.latex(
        r"\mathrm{Índice}="
        r"\frac{\mathrm{Ausência\ atual}}"
        r"{\mathrm{Intervalo\ médio\ histórico}}"
    )

    st.caption(
        "Índice 1,0: ausência igual à média histórica. "
        "Índice 2,0: ausência duas vezes maior."
    )

    mostrar_ranking(
        dados=pesquisar(validos, busca),
        metrica="indice_ausencia",
        eixo="Índice de ausência",
        chave="ordem_a2_indice",
        cores=cores,
        casas=2,
        referencia=1
    )