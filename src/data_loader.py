from __future__ import annotations

from pathlib import Path

import pandas as pd

from .preprocessing import COLUNAS_FINAIS


BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = BASE_DIR / "data" / "processed"
PROCESSED_PATTERN = "conab_prohort_*_ceasa_es.csv"
SAMPLE_PATH = BASE_DIR / "data" / "sample" / "dados_exemplo_conab_prohort_2025.csv"


def _normalizar_base(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for coluna in COLUNAS_FINAIS:
        if coluna not in df.columns:
            df[coluna] = pd.NA
    df["mes"] = pd.to_numeric(df["mes"], errors="coerce").astype("Int64")
    df["ano"] = pd.to_numeric(df["ano"], errors="coerce").astype("Int64")
    df["preco_medio_kg"] = pd.to_numeric(df["preco_medio_kg"], errors="coerce")
    df["quantidade_kg"] = pd.to_numeric(df["quantidade_kg"], errors="coerce")
    return df[COLUNAS_FINAIS]


def carregar_dados() -> tuple[pd.DataFrame, bool, str | None]:
    arquivos_processados = sorted(PROCESSED_DIR.glob(PROCESSED_PATTERN))
    if arquivos_processados:
        frames = [_normalizar_base(pd.read_csv(caminho)) for caminho in arquivos_processados]
        nomes = ", ".join(caminho.name for caminho in arquivos_processados)
        return pd.concat(frames, ignore_index=True), False, nomes

    if SAMPLE_PATH.exists():
        return _normalizar_base(pd.read_csv(SAMPLE_PATH)), True, str(SAMPLE_PATH)
    return pd.DataFrame(columns=COLUNAS_FINAIS), False, None
