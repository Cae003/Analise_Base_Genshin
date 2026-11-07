
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from paginas.dados import indice_versao


HOVER_COLS = [
    "personagem",
    "raridade_label",
    "arma",
    "elemento",
    "modelo_3d",
    "regiao",
    "funcoes_time",
    "lancamento_label",
    "idade_label",
    "qtd_banners_label",
    "periodo_ultimo_banner",
    "versao_ultimo_banner",
    "ausencia_label",
    "media_label",
    "mediana_label",
    "indice_label",
    "arconte_label",
    "padrao_label",
    "pulls_label",
    "copias_label",
    "distancia_label",
    "status_elegibilidade"
]

HOVER = (
    "<b>%{customdata[0]}</b>"
    "<br>Raridade: %{customdata[1]}"
    "<br>Arma: %{customdata[2]}"
    "<br>Elemento: %{customdata[3]}"
    "<br>Modelo: %{customdata[4]}"
    "<br>Região: %{customdata[5]}"
    "<br>Funções: %{customdata[6]}"
    "<br>Lançamento: %{customdata[7]}"
    "<br>Idade: %{customdata[8]} dias"
    "<br>Banners: %{customdata[9]}"
    "<br>Último período: %{customdata[10]}"
    "<br>Última versão: %{customdata[11]}"
    "<br>Ausência: %{customdata[12]} dias"
    "<br>Intervalo médio: %{customdata[13]} dias"
    "<br>Mediana: %{customdata[14]} dias"
    "<br>Índice de ausência: %{customdata[15]}"
    "<br>Arconte: %{customdata[16]}"
    "<br>Banner padrão: %{customdata[17]}"
    "<br>Pulls: %{customdata[18]}"
    "<br>Média de cópias: %{customdata[19]}"
    "<br>Distância até 6.4: %{customdata[20]}"
    "<br>Elegibilidade: %{customdata[21]}"
    "<extra></extra>"
)


def pesquisar(dados, busca):
    if not busca.strip():
        return dados.copy()

    return dados[
        dados["personagem"]
        .astype(str)
        .str.contains(
            busca.strip(),
            case=False,
            regex=False,
            na=False
        )
    ].copy()


def ordenar_ranking(dados, metrica, chave):
    escolha = st.radio(
        "Ordenar personagens por",
        [
            "Métrica do gráfico",
            "Idade (mais novos primeiro)",
            "Idade (mais antigos primeiro)"
        ],
        horizontal=True,
        key=chave
    )

    if escolha == "Idade (mais novos primeiro)":
        return dados.sort_values(
            ["idade_dias", metrica],
            ascending=[True, False],
            na_position="last"
        )

    if escolha == "Idade (mais antigos primeiro)":
        return dados.sort_values(
            ["idade_dias", metrica],
            ascending=[False, False],
            na_position="last"
        )

    return dados.sort_values(
        [metrica, "idade_dias"],
        ascending=[False, True],
        na_position="last"
    )


def mostrar_ranking(
    dados,
    metrica,
    eixo,
    chave,
    cores,
    casas=0,
    referencia=None
):
    dados = dados.replace(
        [np.inf, -np.inf],
        np.nan
    ).dropna(subset=[metrica])

    dados = ordenar_ranking(
        dados,
        metrica,
        chave
    )

    if dados.empty:
        st.info("Nenhum personagem encontrado.")
        return

    fig = px.bar(
        dados,
        x=metrica,
        y="personagem",
        orientation="h",
        color="raridade_label",
        color_discrete_map=cores,
        text=metrica,
        custom_data=HOVER_COLS
    )

    fig.update_traces(
        texttemplate=f"%{{text:.{casas}f}}",
        textposition="outside",
        cliponaxis=False,
        hovertemplate=HOVER
    )

    if referencia is not None:
        fig.add_vline(
            x=referencia,
            line_dash="dash",
            line_color="#888888",
            annotation_text="Referência = 1"
        )

    teto = max(
        float(dados[metrica].max()),
        referencia or 0,
        0.01
    )

    fig.update_layout(
        height=max(
            480,
            31 * len(dados) + 125
        ),
        xaxis={
            "title": eixo,
            "range": [0, teto * 1.19]
        },
        yaxis={
            "title": "",
            "categoryorder": "array",
            "categoryarray": (
                dados["personagem"]
                .iloc[::-1]
                .tolist()
            )
        },
        legend_title="Raridade",
        hoverlabel={"align": "left"},
        margin={"r": 95}
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


def mostrar_dispersao(
    dados,
    x,
    y,
    eixo_x,
    eixo_y,
    busca,
    cores,
    altura=600
):
    dados = dados.dropna(
        subset=[x, y, "raridade_label"]
    )

    if dados.empty:
        st.info("Sem dados suficientes.")
        return

    fig = px.scatter(
        dados,
        x=x,
        y=y,
        color="raridade_label",
        color_discrete_map=cores,
        custom_data=HOVER_COLS,
        labels={
            x: eixo_x,
            y: eixo_y,
            "raridade_label": "Raridade"
        }
    )

    fig.update_traces(
        marker={
            "size": 11,
            "opacity": (
                0.25 if busca.strip() else 0.8
            )
        },
        hovertemplate=HOVER
    )

    if busca.strip():
        destaque = pesquisar(
            dados,
            busca
        )

        if not destaque.empty:
            fig.add_trace(
                go.Scatter(
                    x=destaque[x],
                    y=destaque[y],
                    mode="markers+text",
                    text=destaque["personagem"],
                    textposition="top center",
                    name="Personagem pesquisado",
                    marker={
                        "symbol": "diamond",
                        "size": 18,
                        "color": [
                            cores.get(
                                raridade,
                                "#888888"
                            )
                            for raridade in destaque[
                                "raridade_label"
                            ]
                        ],
                        "line": {
                            "color": "white",
                            "width": 2
                        }
                    },
                    customdata=destaque[
                        HOVER_COLS
                    ].astype(str).to_numpy(),
                    hovertemplate=HOVER
                )
            )

    fig.update_layout(
        height=altura,
        legend_title="Raridade",
        hoverlabel={"align": "left"}
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


def mostrar_linha_tempo(
    aparicoes,
    todas_aparicoes,
    base,
    busca,
    cores
):
    st.subheader(
        "3. Linha do tempo — Aparições por versão"
    )

    st.write(
        "Selecione personagens para acompanhar "
        "seus históricos. Sem seleção, todos os "
        "personagens dos filtros serão exibidos."
    )

    opcoes = sorted(
        base["personagem"]
        .astype(str)
        .unique()
        .tolist()
    )

    chave = "personagens_linha_tempo"

    if chave not in st.session_state:
        st.session_state[chave] = []

    st.session_state[chave] = [
        nome
        for nome in st.session_state[chave]
        if nome in opcoes
    ]

    selecionados = st.multiselect(
        "Personagens na linha do tempo",
        options=opcoes,
        key=chave,
        placeholder=(
            "Nenhum selecionado = todos"
        )
    )

    nomes = (
        selecionados
        if selecionados
        else opcoes
    )

    if busca.strip():
        encontrados = set(
            pesquisar(base, busca)["personagem"]
        )

        nomes = [
            nome
            for nome in nomes
            if nome in encontrados
        ]

    dados = aparicoes[
        aparicoes["personagem"].isin(nomes)
    ].copy()

    if dados.empty:
        st.info("Nenhuma aparição encontrada.")
        return

    dados["indice"] = dados[
        "versao"
    ].apply(indice_versao)

    dados = dados.dropna(
        subset=["indice"]
    )

    ordem = st.radio(
        "Ordenar personagens por",
        [
            "Idade (mais novos primeiro)",
            "Idade (mais antigos primeiro)",
            "Nome"
        ],
        horizontal=True,
        key="ordem_linha_tempo"
    )

    personagens_df = base[
        base["personagem"].isin(nomes)
    ].copy()

    if ordem == "Idade (mais novos primeiro)":
        personagens_df = personagens_df.sort_values(
            ["idade_dias", "personagem"],
            ascending=[True, True]
        )

    elif ordem == "Idade (mais antigos primeiro)":
        personagens_df = personagens_df.sort_values(
            ["idade_dias", "personagem"],
            ascending=[False, True]
        )

    else:
        personagens_df = personagens_df.sort_values(
            "personagem"
        )

    personagens = personagens_df[
        "personagem"
    ].tolist()

    fig = go.Figure()

    for nome in personagens:
        parte = dados[
            dados["personagem"] == nome
        ].sort_values("indice")

        if len(parte) > 1:
            fig.add_trace(
                go.Scatter(
                    x=parte["indice"],
                    y=parte["personagem"],
                    mode="lines",
                    line={
                        "color": "rgba(140,140,140,0.35)",
                        "width": 1.5
                    },
                    hoverinfo="skip",
                    showlegend=False
                )
            )

    for raridade, cor in cores.items():
        parte = dados[
            dados["raridade_label"] == raridade
        ].copy()

        if parte.empty:
            continue

        fig.add_trace(
            go.Scatter(
                x=parte["indice"],
                y=parte["personagem"],
                mode="markers",
                name=raridade,
                marker={
                    "size": 11,
                    "color": cor,
                    "line": {
                        "color": "white",
                        "width": 1
                    }
                },
                customdata=parte[
                    ["versao", "periodo"]
                ].astype(str).to_numpy(),
                hovertemplate=(
                    "<b>%{y}</b>"
                    "<br>Versão: %{customdata[0]}"
                    "<br>Período: %{customdata[1]}"
                    "<extra></extra>"
                )
            )
        )

    versoes = todas_aparicoes[
        ["versao"]
    ].drop_duplicates().copy()

    versoes["indice"] = versoes[
        "versao"
    ].apply(indice_versao)

    versoes = versoes.dropna(
        subset=["indice"]
    ).sort_values("indice")

    fig.update_layout(
        height=max(
            600,
            31 * len(personagens) + 150
        ),
        xaxis={
            "tickmode": "array",
            "tickvals": versoes["indice"].tolist(),
            "ticktext": versoes["versao"].tolist(),
            "tickangle": -45,
            "title": "Versão do jogo"
        },
        yaxis={
            "categoryorder": "array",
            "categoryarray": personagens[::-1],
            "title": ""
        },
        legend_title="Raridade",
        hoverlabel={"align": "left"}
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )