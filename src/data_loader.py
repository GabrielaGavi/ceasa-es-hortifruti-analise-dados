from __future__ import annotations

from pathlib import Path

import pandas as pd

from .preprocessing import COLUNAS_FINAIS


PROCESSED_PATH = Path("data/processed/conab_prohort_2025_ceasa_es.csv")
SAMPLE_PATH = Path("data/sample/dados_exemplo_conab_prohort_2025.csv")


def carregar_dados() -> tuple[pd.DataFrame, bool, Path | None]:
    for caminho, ficticio in [(PROCESSED_PATH, False), (SAMPLE_PATH, True)]:
        if caminho.exists():
            df = pd.read_csv(caminho)
            for coluna in COLUNAS_FINAIS:
                if coluna not in df.columns:
                    df[coluna] = pd.NA
            df["mes"] = pd.to_numeric(df["mes"], errors="coerce").astype("Int64")
            df["ano"] = pd.to_numeric(df["ano"], errors="coerce").astype("Int64")
            df["preco_medio_kg"] = pd.to_numeric(df["preco_medio_kg"], errors="coerce")
            df["quantidade_kg"] = pd.to_numeric(df["quantidade_kg"], errors="coerce")
            return df[COLUNAS_FINAIS], ficticio, caminho
    return pd.DataFrame(columns=COLUNAS_FINAIS), False, None
