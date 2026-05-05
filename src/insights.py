from __future__ import annotations

import pandas as pd

from .metrics import maior_alta_mensal, maior_queda_mensal, preco_medio_anual_produto, quantidade_total_produto, volatilidade_preco


def _linha_top(df: pd.DataFrame, coluna: str) -> pd.Series | None:
    base = df.dropna(subset=[coluna])
    if base.empty:
        return None
    return base.sort_values(coluna, ascending=False).iloc[0]


def gerar_insights_gerais(df: pd.DataFrame) -> list[str]:
    insights = []
    top_preco = _linha_top(preco_medio_anual_produto(df), "preco_medio_anual")
    top_qtd = _linha_top(quantidade_total_produto(df), "quantidade_total_kg")
    top_vol = _linha_top(volatilidade_preco(df), "volatilidade_preco")
    if top_preco is not None:
        insights.append(f"Na amostra analisada, {top_preco['produto']} apresentou o maior preço médio anual.")
    if top_qtd is not None:
        insights.append(f"A análise preliminar indica {top_qtd['produto']} como produto de maior quantidade comercializada.")
    if top_vol is not None:
        insights.append(f"{top_vol['produto']} teve a maior volatilidade de preço na amostra, comportamento que merece investigação posterior.")
    return insights


def gerar_insights_precos(df: pd.DataFrame) -> list[str]:
    insights = []
    alta = maior_alta_mensal(df, 1)
    queda = maior_queda_mensal(df, 1)
    if not alta.empty:
        row = alta.iloc[0]
        insights.append(f"A maior alta mensal observada foi de {row['variacao_percentual']:.1f}% para {row['produto']}.")
    if not queda.empty:
        row = queda.iloc[0]
        insights.append(f"A maior queda mensal observada foi de {row['variacao_percentual']:.1f}% para {row['produto']}.")
    return insights


def gerar_insights_quantidade(df: pd.DataFrame) -> list[str]:
    top_qtd = _linha_top(quantidade_total_produto(df), "quantidade_total_kg")
    if top_qtd is None:
        return []
    return [f"{top_qtd['produto']} apresentou a maior quantidade comercializada na amostra analisada."]


def gerar_insights_modelos(df_alertas: pd.DataFrame, df_clusters: pd.DataFrame) -> list[str]:
    insights = []
    if not df_alertas.empty:
        insights.append(f"Foram identificados {len(df_alertas)} pontos de atenção por variação incomum de preço.")
    if not df_clusters.empty:
        insights.append(f"O K-Means agrupou {df_clusters['produto'].nunique()} produtos em {df_clusters['cluster'].nunique()} grupos preliminares.")
    return insights
