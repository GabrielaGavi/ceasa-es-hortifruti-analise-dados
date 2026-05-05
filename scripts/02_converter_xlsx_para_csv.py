from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.conab_parser import consolidar_xlsx, listar_xlsx


RAW_DIR = ROOT / "data/raw/conab_prohort_2025"
SAIDA = ROOT / "data/processed/conab_prohort_2025_ceasa_es.csv"
SAMPLE = ROOT / "data/sample/dados_exemplo_conab_prohort_2025.csv"


def criar_sample() -> None:
    dados = pd.DataFrame(
        [
            [2025, 1, "CEASA/ES - Vitória", "BANANA PRATA", "Frutas", 4.20, 12000, "dataset_ficticio", "exemplo"],
            [2025, 2, "CEASA/ES - Vitória", "BANANA PRATA", "Frutas", 4.55, 11800, "dataset_ficticio", "exemplo"],
            [2025, 3, "CEASA/ES - Vitória", "BANANA PRATA", "Frutas", 5.60, 11000, "dataset_ficticio", "exemplo"],
            [2025, 1, "CEASA/ES - Vitória", "TOMATE", "Hortaliças", 6.10, 9000, "dataset_ficticio", "exemplo"],
            [2025, 2, "CEASA/ES - Vitória", "TOMATE", "Hortaliças", 4.80, 12500, "dataset_ficticio", "exemplo"],
            [2025, 3, "CEASA/ES - Vitória", "TOMATE", "Hortaliças", 5.10, 11900, "dataset_ficticio", "exemplo"],
            [2025, 1, "CEASA/ES - Vitória", "BATATA INGLESA", "Hortaliças", 3.30, 15000, "dataset_ficticio", "exemplo"],
            [2025, 2, "CEASA/ES - Vitória", "BATATA INGLESA", "Hortaliças", 3.45, 15200, "dataset_ficticio", "exemplo"],
            [2025, 3, "CEASA/ES - Vitória", "BATATA INGLESA", "Hortaliças", 3.20, 16000, "dataset_ficticio", "exemplo"],
        ],
        columns=["ano", "mes", "ceasa", "produto", "categoria", "preco_medio_kg", "quantidade_kg", "fonte_arquivo", "fonte_aba"],
    )
    SAMPLE.parent.mkdir(parents=True, exist_ok=True)
    dados.to_csv(SAMPLE, index=False, encoding="utf-8")
    print(f"Nenhum XLSX encontrado. Dataset fictício criado em {SAMPLE}")


if __name__ == "__main__":
    if not listar_xlsx(RAW_DIR):
        criar_sample()
        sys.exit(0)
    df = consolidar_xlsx(RAW_DIR)
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(SAIDA, index=False, encoding="utf-8")
    print(f"CSV consolidado salvo em {SAIDA} com {len(df)} registros.")
