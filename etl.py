import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Função para separar o início e o fim de cada período
def separar_periodo(periodo):
    inicio, fim = periodo.split(" – ")

    inicio = pd.to_datetime(inicio, format="%B %d, %Y")
    fim = pd.to_datetime(fim, format="%B %d, %Y")

    return inicio, fim

def etl(df):
    import ast
    
    # Criando uma cópia para trabalhar
    df_copyC = df.copy()

    """# Visualizando as primeiras linhas
    '''
    # Dúvida para o Professor
    Ao visualizar a tabela por ter colunas de mais ele coloca "..." e pula para as colunas finais. 
    Tive que abrir em um power BI da vida para ver todas as colunas e entender cada uma delas.
    Daí queria saber se não tem como ter uma visualização melhor de uma tabela com muitas colunas
    '''
    print(df_copyC.head(10))
    print(df_copyC["release_date"])

    # Quantidade de linhas e colunas
    print("Dimensões da base:", df_copyC.shape)

    # Nomes das colunas
    print("\nColunas:")
    print(df_copyC.columns.tolist())

    # Tipos de dados e valores não nulos
    print("\nInformações da base:")
    df_copyC.info()
    print()

    # Estatísticas descritivas (.T Transpõe a Tabela)
    print(df_copyC.describe(include="all").T)
    print()

    # Quantidade de valores ausentes por coluna
    valores_ausentes = df_copyC.isnull().sum()

    # Percentual de valores ausentes
    percentual_ausente = (df_copyC.isnull().mean() * 100).round(0)

    # Criando uma tabela de diagnóstico
    diagnostico_ausentes = pd.DataFrame({
        "Valores ausentes": valores_ausentes,
        "Percentual (%)": percentual_ausente
    })
    print(diagnostico_ausentes)

    # Quantidade de linhas completamente duplicadas
    print("\n\nLinhas duplicadas:", df_copyC.duplicated().sum())"""


    #COMEÇO DAS ALTERAÇÕES

    # Removendo a coluna de índice antigo
    df_copyC = df_copyC.drop(columns=["Unnamed: 0"])

    # Conferindo a alteração
    print(df_copyC.shape)

    # Traduzindo nomes colunas
    df_copyC = df_copyC.rename(columns={
        "name": "personagem",
        "rarity": "raridade",
        "weapon": "arma",
        "element": "elemento",
        "3D-model": "modelo_3d", #
        "region": "regiao",
        "release_date": "data_lancamento",
        "days_since_release": "dias_desde_lancamento",
        "banner_versions": "versoes_banners",
        "banner_dates": "periodos_banners", #
        "roles": "funcoes_time", #
        "constellation_0_pull": "pulls_c0",
        "constellation_1_pull": "pulls_c1",
        "constellation_2_pull": "pulls_c2",
        "constellation_3_pull": "pulls_c3",
        "constellation_4_pull": "pulls_c4",
        "constellation_5_pull": "pulls_c5",
        "constellation_6_pull": "pulls_c6",
        "constellation_7_pull": "pulls_c7",
        "asc_stat_bonus_category": "atributo_ascensao",
        "lvl_90_HP": "lvl_90_HP", #
        "lvl_90_ATK": "lvl_90_ATK", #
        "lvl_90_DEF": "lvl_90_DEF", #
        "duplicate_rate": "taxa_duplicatas",
        "c6_rate": "taxa_c6",
        "avg_copies_per_player": "media_copias_jogador",
        "num_banners": "qtd_banners", #
        "months_since_release": "meses_desde_lancamento",
        "is_standard_banner": "is_banner_padrao", #
        "is_archon": "is_arconte", #
        "pulled_count": "total_pulls"
    })

    print(df_copyC.columns.tolist())



    # Verificando pulls_totais batem com a soma c0 a c7
    # Colunas que representam os pulls por constelação
    colunas_pulls = [
        "pulls_c0",
        "pulls_c1",
        "pulls_c2",
        "pulls_c3",
        "pulls_c4",
        "pulls_c5",
        "pulls_c6",
        "pulls_c7"
    ]

    '''# Somando os pulls de todas as constelações
    df_copyC["total_pulls_calculado"] = df_copyC[colunas_pulls].sum(axis=1)

    # Comparando com o total original
    df_copyC["diferenca_pulls"] = (
        df_copyC["total_pulls"] - df_copyC["total_pulls_calculado"]
    )

    print(df_copyC[["personagem", "total_pulls", "total_pulls_calculado",
            "diferenca_pulls"]].head(15))

    print("\nDiferenças encontradas:",
        (df_copyC["diferenca_pulls"] != 0).sum())'''

    # Remover o total original após ver inconsistencia
    df_copyC = df_copyC.drop(columns=["total_pulls"])

    # Criar novamente o total pela soma das constelações
    df_copyC["total_pulls"] = df_copyC[colunas_pulls].sum(axis=1)

    # Conferir os resultados
    print(df_copyC[["personagem", "total_pulls"]].head())



    # ALteração Tipo Data de Lançamento
    # Visualizar exemplos de datas de lançamento
    print("DATAS DE LANÇAMENTO:")
    print(df_copyC["data_lancamento"].head(10))

    # Converter a data de lançamento para datetime
    df_copyC["data_lancamento"] = pd.to_datetime(
        df_copyC["data_lancamento"],
        format="%Y-%m-%d",
        errors="coerce"
    )

    # Conferir o tipo e possíveis erros
    print(df_copyC["data_lancamento"].dtype)

    print(
        "Datas inválidas:",
        df_copyC["data_lancamento"].isna().sum()
    )



    # Tradução linhas
    # Valores existentes nas colunas categóricas
    colunas_categoricas = [
        "arma",
        "modelo_3d",
        "atributo_ascensao"
    ]

    for coluna in colunas_categoricas:
        print(f"\n--- {coluna.upper()} ---")
        print(df_copyC[coluna].unique())

    # ARMAS
    traducao_armas = {
        "Sword": "Espada",
        "Catalyst": "Catalisador",
        "Claymore": "Espadão",
        "Bow": "Arco",
        "Polearm": "Lança"
    }

    df_copyC["arma"] = df_copyC["arma"].replace(traducao_armas)

    # Modelos 3D
    traducao_modelos = {
        "Medium Female": "Feminino Médio",
        "Medium Male": "Masculino Médio",
        "Tall Female": "Feminino Alto",
        "Short Female": "Feminino Baixo",
        "Tall Male": "Masculino Alto"
    }

    df_copyC["modelo_3d"] = df_copyC["modelo_3d"].replace(traducao_modelos)

    # Atributos de Ascensão
    traducao_atributos = {
        "Anemo DMG Bonus": "Bônus de Dano Anemo",
        "CRIT Rate": "Taxa Crítica",
        "ATK%": "Ataque (%)",
        "Dendro DMG Bonus": "Bônus de Dano Dendro",
        "Healing Bonus": "Bônus de Cura",
        "CRIT DMG": "Dano Crítico",
        "Geo DMG Bonus": "Bônus de Dano Geo",
        "HP%": "Vida (%)",
        "DEF%": "Defesa (%)",
        "Energy Recharge": "Recarga de Energia",
        "Cryo DMG Bonus": "Bônus de Dano Cryo",
        "Pyro DMG Bonus": "Bônus de Dano Pyro",
        "Physical DMG Bonus": "Bônus de Dano Físico",
        "Elemental Mastery": "Proficiência Elemental",
        "Electro DMG Bonus": "Bônus de Dano Electro",
        "Hydro DMG Bonus": "Bônus de Dano Hydro"
    }

    df_copyC["atributo_ascensao"] = df_copyC["atributo_ascensao"].replace(
        traducao_atributos
    )

    print(df_copyC["arma"].unique())
    print(df_copyC["modelo_3d"].unique())
    print(df_copyC["atributo_ascensao"].unique())



    # Trantando as datas dos bunners e suas versões
    # Visualizar exemplos de versões
    print("\nVERSÕES DOS BANNERS:")
    print(df_copyC["versoes_banners"].head(10))

    # Visualizar exemplos de datas dos banners
    print("\nDATAS DOS BANNERS:")
    print(df_copyC["periodos_banners"].head(10))

    # Converter textos que representam listas em listas Python
    df_copyC["versoes_banners"] = df_copyC["versoes_banners"].apply(ast.literal_eval)

    df_copyC["periodos_banners"] = df_copyC["periodos_banners"].apply(ast.literal_eval)

    # Conferir os resultados
    print(df_copyC["versoes_banners"].iloc[0])
    print(type(df_copyC["versoes_banners"].iloc[0]))

    print(df_copyC["periodos_banners"].iloc[0])
    print(type(df_copyC["periodos_banners"].iloc[0]))

    # Criar listas de datas de início e fim
    df_copyC["datas_inicio_banners"] = df_copyC["periodos_banners"].apply(
        lambda lista: [separar_periodo(p)[0] for p in lista]
    )

    df_copyC["datas_fim_banners"] = df_copyC["periodos_banners"].apply(
        lambda lista: [separar_periodo(p)[1] for p in lista]
    )

    # Conferir um personagem
    print("Períodos originais:")
    print(df_copyC["periodos_banners"].iloc[0])

    print("\nDatas de início:")
    print(df_copyC["datas_inicio_banners"].iloc[0])

    print("\nDatas de fim:")
    print(df_copyC["datas_fim_banners"].iloc[0])



    # Criando colunas sobre o ultimo banner
    # Coluna "ultimo_banner"
    df_copyC["ultimo_banner"] = df_copyC["datas_fim_banners"].apply(max)

    print(df_copyC[["personagem", "ultimo_banner"]].head(10))

    # Encontrar a data final mais recente entre todos os banners
    data_referencia = df_copyC['ultimo_banner'].max()
    print("Data de referência:", data_referencia)

    # Coluna "dias_desde_ultimo_banner"
    df_copyC["dias_desde_ultimo_banner"] = (
        data_referencia - df_copyC["ultimo_banner"]
    ).dt.days

    # Coluna "meses_desde_ultimo_banner"
    df_copyC["meses_desde_ultimo_banner"] = (
        df_copyC["dias_desde_ultimo_banner"] / 30.50
    )

    print(df_copyC[["personagem", "ultimo_banner","dias_desde_ultimo_banner", "meses_desde_ultimo_banner"]].head(10))
    print()
    print(df_copyC.head(10))
    return df_copyC