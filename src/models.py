from __future__ import annotations

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from .metrics import (
    preco_medio_anual_produto,
    quantidade_media_mensal_produto,
    quantidade_total_produto,
    variacao_percentual_mensal,
    volatilidade_preco,
)


def detectar_variacoes_incomuns(df: pd.DataFrame, limite_percentual: float = 20.0) -> pd.DataFrame:
    variacoes = variacao_percentual_mensal(df)
    alertas = variacoes[variacoes["variacao_percentual"].abs() >= limite_percentual].copy()
    alertas["tipo"] = alertas["variacao_percentual"].apply(lambda v: "alta" if v > 0 else "queda")
    alertas["ponto_atencao"] = "variacao incomum"
    return alertas.sort_values("variacao_percentual", key=lambda s: s.abs(), ascending=False)


def preparar_features_kmeans(df: pd.DataFrame) -> pd.DataFrame:
    variacoes = variacao_percentual_mensal(df)
    variacao_max = (
        variacoes.groupby("produto")["variacao_percentual"]
        .apply(lambda s: s.abs().max())
        .reset_index(name="variacao_maxima_absoluta")
    )
    features = preco_medio_anual_produto(df)
    for parcial in [
        volatilidade_preco(df),
        variacao_max,
        quantidade_media_mensal_produto(df),
        quantidade_total_produto(df),
    ]:
        features = features.merge(parcial, on="produto", how="left")
    features = features.fillna(0)
    colunas_numericas = [
        "preco_medio_anual",
        "volatilidade_preco",
        "variacao_maxima_absoluta",
        "quantidade_media_kg",
        "quantidade_total_kg",
    ]
    return features.dropna(subset=colunas_numericas)


def aplicar_kmeans(df_features: pd.DataFrame, n_clusters: int = 3) -> tuple[pd.DataFrame, float | None]:
    if df_features.empty or len(df_features) < 2:
        return pd.DataFrame(), None
    n_clusters = max(2, min(int(n_clusters), len(df_features)))
    colunas = [
        "preco_medio_anual",
        "volatilidade_preco",
        "variacao_maxima_absoluta",
        "quantidade_media_kg",
        "quantidade_total_kg",
    ]
    x = df_features[colunas].fillna(0)
    x_scaled = StandardScaler().fit_transform(x)
    modelo = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clusters = modelo.fit_predict(x_scaled)
    saida = df_features.copy()
    saida["cluster"] = clusters
    score = None
    if len(df_features) > n_clusters and n_clusters > 1:
        score = float(silhouette_score(x_scaled, clusters))
    return saida, score


def interpretar_clusters(df_clusters: pd.DataFrame) -> dict[int, str]:
    if df_clusters.empty:
        return {}
    medias = df_clusters.groupby("cluster").mean(numeric_only=True)
    interpretacoes = {}
    for cluster, row in medias.iterrows():
        partes = []
        if row.get("volatilidade_preco", 0) >= medias["volatilidade_preco"].median():
            partes.append("produtos com maior volatilidade relativa")
        else:
            partes.append("produtos mais estáveis na amostra")
        if row.get("quantidade_total_kg", 0) >= medias["quantidade_total_kg"].median():
            partes.append("maior volume comercializado")
        if row.get("preco_medio_anual", 0) >= medias["preco_medio_anual"].median():
            partes.append("maior preço médio")
        interpretacoes[int(cluster)] = "; ".join(partes) + "."
    return interpretacoes
