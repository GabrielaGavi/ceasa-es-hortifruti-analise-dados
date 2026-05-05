from __future__ import annotations

import numpy as np
import pandas as pd


def preco_medio_mensal(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby(["produto", "ano", "mes"], as_index=False)["preco_medio_kg"].mean()


def preco_medio_anual_produto(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("produto", as_index=False)["preco_medio_kg"].mean().rename(columns={"preco_medio_kg": "preco_medio_anual"})


def quantidade_total_produto(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("produto", as_index=False)["quantidade_kg"].sum(min_count=1).rename(columns={"quantidade_kg": "quantidade_total_kg"})


def quantidade_media_mensal_produto(df: pd.DataFrame) -> pd.DataFrame:
    mensal = df.groupby(["produto", "ano", "mes"], as_index=False)["quantidade_kg"].sum(min_count=1)
    return mensal.groupby("produto", as_index=False)["quantidade_kg"].mean().rename(columns={"quantidade_kg": "quantidade_media_kg"})


def variacao_percentual_mensal(df: pd.DataFrame) -> pd.DataFrame:
    mensal = preco_medio_mensal(df).sort_values(["produto", "ano", "mes"])
    mensal["variacao_percentual"] = mensal.groupby("produto")["preco_medio_kg"].pct_change() * 100
    return mensal


def amplitude_preco(df: pd.DataFrame) -> pd.DataFrame:
    agg = df.groupby("produto")["preco_medio_kg"].agg(["min", "max"]).reset_index()
    agg["amplitude_preco"] = agg["max"] - agg["min"]
    return agg[["produto", "amplitude_preco"]]


def volatilidade_preco(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("produto", as_index=False)["preco_medio_kg"].std().rename(columns={"preco_medio_kg": "volatilidade_preco"})


def maior_alta_mensal(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    return variacao_percentual_mensal(df).dropna(subset=["variacao_percentual"]).sort_values("variacao_percentual", ascending=False).head(n)


def maior_queda_mensal(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    return variacao_percentual_mensal(df).dropna(subset=["variacao_percentual"]).sort_values("variacao_percentual").head(n)


def correlacao_preco_quantidade(df: pd.DataFrame) -> float | None:
    base = df[["preco_medio_kg", "quantidade_kg"]].dropna()
    if len(base) < 3 or base["preco_medio_kg"].nunique() < 2 or base["quantidade_kg"].nunique() < 2:
        return None
    valor = base["preco_medio_kg"].corr(base["quantidade_kg"])
    return None if np.isnan(valor) else float(valor)


def extremos_mensais_por_produto(df: pd.DataFrame) -> pd.DataFrame:
    mensal = (
        df.groupby(["produto", "mes"], as_index=False)
        .agg(preco_medio_kg=("preco_medio_kg", "mean"), quantidade_kg=("quantidade_kg", "sum"))
        .dropna(subset=["produto", "mes"])
    )
    registros = []
    for produto, grupo in mensal.groupby("produto"):
        item = {"produto": produto}
        preco = grupo.dropna(subset=["preco_medio_kg"])
        quantidade = grupo.dropna(subset=["quantidade_kg"])
        if not preco.empty:
            maior_preco = preco.loc[preco["preco_medio_kg"].idxmax()]
            menor_preco = preco.loc[preco["preco_medio_kg"].idxmin()]
            item.update(
                {
                    "mes_maior_preco": int(maior_preco["mes"]),
                    "maior_preco_kg": maior_preco["preco_medio_kg"],
                    "mes_menor_preco": int(menor_preco["mes"]),
                    "menor_preco_kg": menor_preco["preco_medio_kg"],
                }
            )
        if not quantidade.empty:
            maior_qtd = quantidade.loc[quantidade["quantidade_kg"].idxmax()]
            menor_qtd = quantidade.loc[quantidade["quantidade_kg"].idxmin()]
            item.update(
                {
                    "mes_maior_quantidade": int(maior_qtd["mes"]),
                    "maior_quantidade_kg": maior_qtd["quantidade_kg"],
                    "mes_menor_quantidade": int(menor_qtd["mes"]),
                    "menor_quantidade_kg": menor_qtd["quantidade_kg"],
                }
            )
        registros.append(item)
    return pd.DataFrame(registros)


def indice_mensal_por_produto(df: pd.DataFrame) -> pd.DataFrame:
    mensal = (
        df.groupby(["produto", "mes"], as_index=False)
        .agg(preco_medio_kg=("preco_medio_kg", "mean"), quantidade_kg=("quantidade_kg", "sum"))
        .dropna(subset=["produto", "mes"])
    )
    if mensal.empty:
        return mensal
    mensal["indice_preco"] = mensal.groupby("produto")["preco_medio_kg"].transform(lambda s: (s / s.mean()) * 100)
    mensal["indice_quantidade"] = mensal.groupby("produto")["quantidade_kg"].transform(lambda s: (s / s.mean()) * 100)
    return mensal
