
import ast
import re
import unicodedata

import numpy as np
import pandas as pd
import streamlit as st


# ============================================================
# FUNÇÕES GERAIS
# ============================================================

def normalizar(valor):
    texto = unicodedata.normalize(
        "NFKD",
        str(valor)
    )

    texto = "".join(
        c for c in texto
        if not unicodedata.combining(c)
    )

    return re.sub(
        r"[^a-z0-9]+",
        "_",
        texto.lower()
    ).strip("_")


def formatar(valor, casas=0):
    try:
        numero = float(valor)

        if not np.isfinite(numero):
            return "Não disponível"

    except (ValueError, TypeError):
        return "Não disponível"

    return (
        f"{numero:,.{casas}f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def ler_lista(valor):
    if isinstance(valor, (list, tuple)):
        return list(valor)

    if valor is None:
        return []

    try:
        if pd.isna(valor):
            return []
    except (TypeError, ValueError):
        return []

    try:
        resultado = ast.literal_eval(str(valor))

        if isinstance(resultado, (list, tuple)):
            return list(resultado)

    except (SyntaxError, ValueError):
        pass

    return []


def tratar_funcoes(valor):
    if isinstance(valor, (list, tuple)):
        return [
            str(item).strip()
            for item in valor
            if str(item).strip()
        ]

    if pd.isna(valor):
        return []

    texto = str(valor).strip()

    if texto.startswith("["):
        lista = ler_lista(texto)

        if lista:
            return [
                str(item).strip()
                for item in lista
                if str(item).strip()
            ]

    return [
        parte.strip()
        for parte in re.split(r"[,;/]", texto)
        if parte.strip()
    ]


def converter_booleanos(serie):
    return (
        serie.astype(str)
        .str.strip()
        .str.lower()
        .isin([
            "1",
            "1.0",
            "true",
            "sim",
            "yes"
        ])
    )


# ============================================================
# VERSÕES
# ============================================================

def romano_para_inteiro(texto):
    valores = {
        "I": 1,
        "V": 5,
        "X": 10,
        "L": 50,
        "C": 100,
        "D": 500,
        "M": 1000
    }

    total = 0
    anterior = 0

    for letra in reversed(texto.upper()):
        atual = valores.get(letra, 0)

        if atual < anterior:
            total -= atual
        else:
            total += atual

        anterior = atual

    return total


def indice_versao(versao):
    """
    Índice cronológico das versões.

    1.0 -> 0
    1.6 -> 6
    2.0 -> 7
    3.0 -> 16
    4.0 -> 25
    5.0 -> 34
    5.8 -> 42
    Luna I -> 43
    Luna V -> 47
    """

    texto = str(versao).strip()

    numero = re.fullmatch(
        r"(\d+)\.(\d+)",
        texto
    )

    if numero:
        principal = int(numero.group(1))
        secundaria = int(numero.group(2))

        if principal == 1 and 0 <= secundaria <= 6:
            return secundaria

        if 2 <= principal <= 5 and 0 <= secundaria <= 8:
            return (
                7
                + (principal - 2) * 9
                + secundaria
            )

        if principal == 6:
            return 43 + secundaria

    luna = re.fullmatch(
        r"Luna\s+([IVXLCDM]+)",
        texto,
        flags=re.IGNORECASE
    )

    if luna:
        return (
            42
            + romano_para_inteiro(luna.group(1))
        )

    return np.nan


# ============================================================
# PERÍODOS DOS BANNERS
# ============================================================

def ler_periodo(texto):
    partes = re.split(
        r"\s+[–—-]\s+",
        str(texto),
        maxsplit=1
    )

    if len(partes) != 2:
        return None

    inicio = pd.to_datetime(
        partes[0].strip(),
        errors="coerce"
    )

    fim = pd.to_datetime(
        partes[1].strip(),
        errors="coerce"
    )

    if pd.isna(inicio) or pd.isna(fim):
        return None

    if inicio > fim:
        return None

    return inicio, fim


def obter_banners(linha):
    versoes = ler_lista(
        linha["versoes_banners"]
    )

    periodos = ler_lista(
        linha["periodos_banners"]
    )

    resultado = []

    for i, descricao in enumerate(periodos):
        datas = ler_periodo(descricao)

        if datas is None:
            continue

        versao = (
            str(versoes[i])
            if i < len(versoes)
            else "Não informada"
        )

        resultado.append({
            "inicio": datas[0],
            "fim": datas[1],
            "periodo": str(descricao),
            "versao": versao
        })

    return sorted(
        resultado,
        key=lambda banner: (
            banner["inicio"],
            banner["fim"]
        )
    )


# ============================================================
# CARREGAR E PREPARAR CSV
# ============================================================

@st.cache_data(show_spinner="Carregando dados...")
def carregar_base(
    origem,
    versao_cache,
    data_corte,
    versao_alvo,
    distancia_minima
):
    original = pd.read_csv(origem)

    df = original.copy()

    df.columns = [
        normalizar(coluna)
        for coluna in df.columns
    ]

    obrigatorias = [
        "personagem",
        "raridade",
        "arma",
        "elemento",
        "modelo_3d",
        "regiao",
        "funcoes_time",
        "data_lancamento",
        "ultimo_banner",
        "qtd_banners",
        "is_arconte",
        "is_banner_padrao",
        "versoes_banners",
        "periodos_banners",
        "total_pulls",
        "media_copias_jogador"
    ]

    faltantes = [
        coluna
        for coluna in obrigatorias
        if coluna not in df.columns
    ]

    if faltantes:
        raise ValueError(
            "Colunas ausentes no CSV: "
            + ", ".join(faltantes)
        )

    for coluna in [
        "data_lancamento",
        "ultimo_banner"
    ]:
        df[coluna] = pd.to_datetime(
            df[coluna],
            errors="coerce"
        )

    numericas = [
        "raridade",
        "qtd_banners",
        "total_pulls",
        "media_copias_jogador",
        "pulls_c0",
        "taxa_c6",
        "taxa_duplicatas"
    ]

    for coluna in numericas:
        if coluna not in df.columns:
            df[coluna] = np.nan

        df[coluna] = pd.to_numeric(
            df[coluna],
            errors="coerce"
        )

    for coluna in [
        "is_arconte",
        "is_banner_padrao"
    ]:
        df[coluna] = converter_booleanos(
            df[coluna]
        )

    df["funcoes_lista"] = df[
        "funcoes_time"
    ].apply(tratar_funcoes)

    df["banners"] = df.apply(
        obter_banners,
        axis=1
    )

    df["raridade_label"] = df[
        "raridade"
    ].map({
        4: "4 estrelas",
        5: "5 estrelas"
    })

    df["idade_dias"] = (
        data_corte - df["data_lancamento"]
    ).dt.days

    df["dias_sem_banner"] = (
        data_corte - df["ultimo_banner"]
    ).dt.days.clip(lower=0)

    df["fim_ultimo_banner"] = pd.to_datetime(
        df["banners"].apply(
            lambda banners: (
                banners[-1]["fim"]
                if banners else pd.NaT
            )
        ),
        errors="coerce"
    )

    df["ausencia_atual"] = (
        data_corte - df["fim_ultimo_banner"]
    ).dt.days.clip(lower=0)

    df["versao_ultimo_banner"] = df[
        "banners"
    ].apply(
        lambda banners: (
            banners[-1]["versao"]
            if banners else "Não informada"
        )
    )

    df["periodo_ultimo_banner"] = df[
        "banners"
    ].apply(
        lambda banners: (
            banners[-1]["periodo"]
            if banners else "Não informado"
        )
    )

    df["lancamento_label"] = (
        df["data_lancamento"]
        .dt.strftime("%d/%m/%Y")
        .fillna("Não informado")
    )

    df["arconte_label"] = np.where(
        df["is_arconte"],
        "Sim",
        "Não"
    )

    df["padrao_label"] = np.where(
        df["is_banner_padrao"],
        "Sim",
        "Não"
    )

    # --------------------------------------------------------
    # TABELA DE APARIÇÕES
    # --------------------------------------------------------

    registros_aparicoes = []
    registros_intervalos = []

    for _, linha in df.iterrows():
        banners = linha["banners"]

        for banner in banners:
            registros_aparicoes.append({
                "personagem": linha["personagem"],
                "raridade": linha["raridade"],
                "raridade_label": linha["raridade_label"],
                "versao": banner["versao"],
                "periodo": banner["periodo"],
                "inicio": banner["inicio"],
                "fim": banner["fim"]
            })

        for anterior, posterior in zip(
            banners,
            banners[1:]
        ):
            dias = (
                posterior["inicio"]
                - anterior["fim"]
            ).days

            if dias < 0:
                continue

            registros_intervalos.append({
                "personagem": linha["personagem"],
                "raridade": linha["raridade"],
                "raridade_label": linha["raridade_label"],
                "dias_intervalo": dias,
                "banner_anterior": anterior["periodo"],
                "banner_posterior": posterior["periodo"],
                "versao_anterior": anterior["versao"],
                "versao_posterior": posterior["versao"]
            })

    aparicoes = pd.DataFrame(
        registros_aparicoes,
        columns=[
            "personagem",
            "raridade",
            "raridade_label",
            "versao",
            "periodo",
            "inicio",
            "fim"
        ]
    )

    intervalos = pd.DataFrame(
        registros_intervalos,
        columns=[
            "personagem",
            "raridade",
            "raridade_label",
            "dias_intervalo",
            "banner_anterior",
            "banner_posterior",
            "versao_anterior",
            "versao_posterior"
        ]
    )

    # --------------------------------------------------------
    # INTERVALOS HISTÓRICOS
    # --------------------------------------------------------

    if not intervalos.empty:
        estatisticas = (
            intervalos.groupby("personagem")[
                "dias_intervalo"
            ]
            .agg(
                intervalo_medio="mean",
                intervalo_mediano="median",
                qtd_intervalos="count"
            )
            .reset_index()
        )

        df = df.merge(
            estatisticas,
            on="personagem",
            how="left",
            validate="one_to_one"
        )

    else:
        df["intervalo_medio"] = np.nan
        df["intervalo_mediano"] = np.nan
        df["qtd_intervalos"] = np.nan

    df["indice_ausencia"] = np.where(
        df["intervalo_medio"] > 0,
        df["ausencia_atual"]
        / df["intervalo_medio"],
        np.nan
    )

    # --------------------------------------------------------
    # ELEGIBILIDADE
    # --------------------------------------------------------

    indice_alvo = indice_versao(
        versao_alvo
    )

    df["indice_ultima_versao"] = df[
        "versao_ultimo_banner"
    ].apply(indice_versao)

    df["distancia_para_alvo"] = (
        indice_alvo
        - df["indice_ultima_versao"]
    )

    # 4★: não existe restrição.
    # 5★: distância mínima de versões.
    df["elegivel_64"] = (
        (df["raridade"] == 4)
        | (
            (df["raridade"] == 5)
            & (
                df["distancia_para_alvo"]
                >= distancia_minima
            )
        )
    )

    df["status_elegibilidade"] = np.select(
        [
            df["raridade"] == 4,
            (
                (df["raridade"] == 5)
                & df["indice_ultima_versao"].isna()
            ),
            df["elegivel_64"]
        ],
        [
            "Elegível — 4★",
            "Indeterminado",
            "Elegível pelo critério"
        ],
        default="Excluído pelo critério"
    )

    # --------------------------------------------------------
    # CAMPOS FORMATADOS PARA HOVER
    # --------------------------------------------------------

    formatacoes = [
        ("idade_dias", "idade_label", 0),
        ("qtd_banners", "qtd_banners_label", 0),
        ("dias_sem_banner", "dias_sem_banner_label", 0),
        ("ausencia_atual", "ausencia_label", 0),
        ("intervalo_medio", "media_label", 1),
        ("intervalo_mediano", "mediana_label", 1),
        ("indice_ausencia", "indice_label", 2),
        ("total_pulls", "pulls_label", 0),
        ("media_copias_jogador", "copias_label", 2),
        ("distancia_para_alvo", "distancia_label", 0)
    ]

    for origem_coluna, destino, casas in formatacoes:
        df[destino] = df[
            origem_coluna
        ].apply(
            lambda valor: formatar(
                valor,
                casas
            )
        )

    return original, df, aparicoes, intervalos