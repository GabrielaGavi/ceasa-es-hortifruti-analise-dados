from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.conab_parser import gerar_relatorio_diagnostico


RAW_DIR = ROOT / "data/raw/conab_prohort_2025"
SAIDA = ROOT / "docs/diagnostico_planilhas.md"


if __name__ == "__main__":
    gerar_relatorio_diagnostico(RAW_DIR, SAIDA)
    print(f"Diagnóstico salvo em {SAIDA}")
