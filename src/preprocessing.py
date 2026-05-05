from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd


MESES = {
    "janeiro": 1,
    "fevereiro": 2,
    "marco": 3,
    "março": 3,
    "abril": 4,
    "maio": 5,
    "junho": 6,
    "julho": 7,
    "agosto": 8,
    "setembro": 9,
    "outubro": 10,
    "novembro": 11,
    "dezembro": 12,
}

COLUNAS_FINAIS = [
    "ano",
    "mes",
    "ceasa",
    "produto",
    "categoria",
    "preco_medio_kg",
    "quantidade_kg",
    "fonte_arquivo",
    "fonte_aba",
]


def normalizar_texto(valor: object) -> str:
    if pd.isna(valor):
        return ""
    texto = str(valor).strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(ch for ch in texto if not unicodedata.combining(ch))
    texto = re.sub(r"\s+", " ", texto)
    return texto


def nome_coluna(valor: object) -> str:
    texto = normalizar_texto(valor)
    texto = re.sub(r"[^a-z0-9]+", "_", texto).strip("_")
    return texto or "coluna"


def mes_por_nome_arquivo(caminho: str | Path) -> int | None:
    nome = normalizar_texto(Path(caminho).stem)
    for mes, numero in MESES.items():
        if normalizar_texto(mes) in nome:
            return numero
    match = re.search(r"(?:^|[_-])(0?[1-9]|1[0-2])(?:[_-]|$)", nome)
    return int(match.group(1)) if match else None


def ano_por_nome_arquivo(caminho: str | Path, padrao: int = 2025) -> int:
    match = re.search(r"(20\d{2})", Path(caminho).stem)
    return int(match.group(1)) if match else padrao


def limpar_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.dropna(how="all")
    df = df.dropna(axis=1, how="all")
    df = df.loc[:, ~df.columns.astype(str).str.match(r"^Unnamed")]
    return df


def remover_linhas_nao_dados(df: pd.DataFrame, produto_col: str | None = None) -> pd.DataFrame:
    if df.empty:
        return df
    df = df.copy()
    if produto_col and produto_col in df.columns:
        produto = df[produto_col].map(normalizar_texto)
        mascara = produto.ne("") & ~produto.str.contains(
            r"^(?:total|subtotal|sub total|fonte|produto|produtos|ceasa|mercado|unidade)$",
            regex=True,
            na=False,
        )
        df = df[mascara]
    return df.dropna(how="all")


def numero_brasileiro(valor: object) -> float:
    if pd.isna(valor):
        return np.nan
    if isinstance(valor, (int, float, np.integer, np.floating)):
        return float(valor)
    texto = str(valor).strip()
    if not texto or texto in {"-", "--", "..."}:
        return np.nan
    texto = re.sub(r"[^\d,.\-]", "", texto)
    if not texto or texto in {"-", ".", ","}:
        return np.nan
    if "," in texto and "." in texto:
        if texto.rfind(",") > texto.rfind("."):
            texto = texto.replace(".", "").replace(",", ".")
        else:
            texto = texto.replace(",", "")
    elif "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    try:
        return float(texto)
    except ValueError:
        return np.nan


def padronizar_produto(valor: object) -> str:
    texto = str(valor).strip() if not pd.isna(valor) else ""
    texto = re.sub(r"\s+", " ", texto)
    return texto.upper()


def padronizar_ceasa(valor: object) -> str:
    texto = normalizar_texto(valor)
    if "vitoria" in texto or "ceasa/es" in texto or "ceasa es" in texto:
        return "CEASA/ES - Vitória"
    return str(valor).strip() if not pd.isna(valor) else ""


def eh_ceasa_es_vitoria(valor: object) -> bool:
    texto = normalizar_texto(valor)
    return (
        "vitoria" in texto
        or "ceasa/es" in texto
        or "ceasa es" in texto
        or ("espirito santo" in texto and "ceasa" in texto)
    )


def finalizar_base(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=COLUNAS_FINAIS)
    df = df.copy()
    for coluna in COLUNAS_FINAIS:
        if coluna not in df.columns:
            df[coluna] = np.nan if coluna in {"preco_medio_kg", "quantidade_kg"} else ""
    df["produto"] = df["produto"].map(padronizar_produto)
    df["ceasa"] = df["ceasa"].map(padronizar_ceasa)
    df["preco_medio_kg"] = df["preco_medio_kg"].map(numero_brasileiro)
    df["quantidade_kg"] = df["quantidade_kg"].map(numero_brasileiro)
    df = df[df["produto"].ne("")]
    df = df[~(df["preco_medio_kg"].isna() & df["quantidade_kg"].isna())]
    return df[COLUNAS_FINAIS].reset_index(drop=True)
