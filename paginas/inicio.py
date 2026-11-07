
import re
import unicodedata

import pandas as pd
import streamlit as st

from paginas.dados import normalizar


MESES = {
    "january": "janeiro",
    "february": "fevereiro",
    "march": "março",
    "april": "abril",
    "may": "maio",
    "june": "junho",
    "july": "julho",
    "august": "agosto",
    "september": "setembro",
    "october": "outubro",
    "november": "novembro",
    "december": "dezembro"
}


def texto_pesquisavel(valor):
    texto = str(valor)
    adicionais = []

    for ingles, portugues in MESES.items():
        if re.search(
            rf"\b{ingles}\b",
            texto,
            flags=re.IGNORECASE
        ):
            adicionais.append(portugues)

    return texto + " " + " ".join(adicionais)


def renderizar(
    original,
    base_completa,
    data_corte
):
    st.title(
        "Bem-vindo ao estudo de banners!"
    )

    st.write(
        "Este dashboard investiga o histórico de "
        "personagens de Genshin Impact para identificar "
        "padrões de ausência, frequência de retorno "
        "e interesse dos jogadores."
    )

    st.subheader(
        "O que observar nas análises?"
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            "**1. Ausência relativa**  \n"
            "Compara a ausência atual com o intervalo "
            "histórico do próprio personagem."
        )

        st.markdown(
            "**2. Idade do personagem**  \n"
            "Personagens mais recentes recebem "
            "prioridade na nossa hipótese, pela possível "
            "relevância no meta atual."
        )

    with col2:
        st.markdown(
            "**3. Frequência histórica**  \n"
            "Mostra se um personagem costuma retornar "
            "rapidamente ou passar muito tempo ausente."
        )

        st.markdown(
            "**4. Interesse dos jogadores**  \n"
            "Os pulls acumulados ajudam a comparar "
            "o interesse registrado na amostra."
        )

    st.info(
        "**Elegibilidade para a 6.4:** personagens 5★ "
        "precisam de uma distância mínima de duas versões "
        "desde a última aparição registrada. "
        "Personagens 4★ não têm essa restrição."
    )

    st.caption(
        "Esses critérios ajudam a formular hipóteses. "
        "Eles não representam probabilidades oficiais "
        "de rerun nem garantem decisões da HoYoverse."
    )

    st.divider()

    st.subheader(
        "Consultar base de dados"
    )

    pesquisa = st.text_input(
        "Pesquisar em qualquer coluna",
        placeholder=(
            "Ex.: Furina, Fontaine, Hydro, agosto..."
        ),
        key="pesquisa_base"
    )

    tabela = original.copy()

    if pesquisa.strip():
        termo = normalizar(pesquisa)

        mascara = tabela.apply(
            lambda linha: any(
                termo in normalizar(
                    texto_pesquisavel(valor)
                )
                for valor in linha
            ),
            axis=1
        )

        tabela = tabela.loc[mascara]

    a, b, c = st.columns(3)

    a.metric(
        "Registros encontrados",
        len(tabela)
    )

    b.metric(
        "Colunas",
        tabela.shape[1]
    )

    c.metric(
        "Total de personagens",
        len(original)
    )

    st.dataframe(
        tabela,
        use_container_width=True,
        hide_index=True,
        height=650
    )

    st.download_button(
        "Exportar CSV filtrado",
        data=tabela.to_csv(
            index=False
        ).encode("utf-8-sig"),
        file_name="genshin_filtrado.csv",
        mime="text/csv"
    )

    st.caption(
        "Data de referência: "
        f"{data_corte.strftime('%d/%m/%Y')}. "
        "A tabela apresenta os dados originais "
        "do CSV, sem aplicar os filtros das análises."
    )