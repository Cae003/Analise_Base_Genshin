
import pandas as pd
import plotly.express as px
import streamlit as st

from paginas.dados import formatar

from paginas.componentes import (
    pesquisar,
    mostrar_ranking,
    mostrar_linha_tempo
)


def renderizar(
    base,
    aparicoes,
    todas_aparicoes,
    intervalos,
    busca,
    cores
):
    st.header(
        "Análise 1 — Ausência e cronologia"
    )

    st.write(
        "Investigamos quais personagens estão há "
        "mais tempo sem aparecer, como variam os "
        "intervalos históricos e em quais versões "
        "cada personagem recebeu banner."
    )

    a, b, c = st.columns(3)

    a.metric(
        "Personagens nos filtros",
        len(base)
    )

    if (
        not base.empty
        and base["dias_sem_banner"].notna().any()
    ):
        maior_ausencia = (
            f"{formatar(base['dias_sem_banner'].max())} dias"
        )
    else:
        maior_ausencia = "—"

    b.metric(
        "Maior ausência",
        maior_ausencia
    )

    c.metric(
        "Intervalos históricos",
        len(intervalos)
    )

    # ========================================================
    # GRÁFICO 1 — AUSÊNCIA
    # ========================================================

    st.subheader(
        "1. Dias desde a última aparição"
    )

    st.write(
        "Ranking dos personagens com maior tempo "
        "desde o último banner registrado."
    )

    mostrar_ranking(
        dados=pesquisar(base, busca),
        metrica="dias_sem_banner",
        eixo="Dias desde a última aparição",
        chave="ordem_a1_ausencia",
        cores=cores
    )

    # ========================================================
    # GRÁFICO 2 — BOXPLOT
    # ========================================================

    st.subheader(
        "2. Distribuição dos intervalos entre banners"
    )

    st.write(
        "Comparamos a distribuição de dias entre "
        "banners consecutivos de personagens 4★ e 5★."
    )

    if intervalos.empty:
        st.info(
            "Não existem intervalos disponíveis "
            "para os filtros selecionados."
        )

    else:
        fig = px.box(
            intervalos,
            x="raridade_label",
            y="dias_intervalo",
            color="raridade_label",
            color_discrete_map=cores,
            points="outliers",
            hover_data=[
                "personagem",
                "banner_anterior",
                "banner_posterior"
            ],
            labels={
                "raridade_label": "Raridade",
                "dias_intervalo": (
                    "Dias entre banners"
                )
            }
        )

        fig.update_layout(
            height=550,
            showlegend=False
        )

        # Adiciona a média como ponto separado.
        for raridade, cor in cores.items():
            parte = intervalos[
                intervalos["raridade_label"]
                == raridade
            ]

            if parte.empty:
                continue

            media = parte[
                "dias_intervalo"
            ].mean()

            fig.add_annotation(
                x=raridade,
                y=media,
                text=(
                    f"Média: {media:.1f} dias"
                ),
                showarrow=True,
                ax=85,
                ay=-25,
                font={"color": cor}
            )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # ========================================================
    # GRÁFICO 3 — LINHA DO TEMPO
    # ========================================================

    mostrar_linha_tempo(
        aparicoes=aparicoes,
        todas_aparicoes=todas_aparicoes,
        base=base,
        busca=busca,
        cores=cores
    )