from __future__ import annotations

from pathlib import Path

import pandas as pd

from .preprocessing import (
    COLUNAS_FINAIS,
    ano_por_nome_arquivo,
    eh_ceasa_es_vitoria,
    finalizar_base,
    limpar_dataframe,
    mes_por_nome_arquivo,
    nome_coluna,
    normalizar_texto,
    numero_brasileiro,
    remover_linhas_nao_dados,
)

HORTALICAS = {"alface", "batata", "cebola", "cenoura", "tomate"}
FRUTAS = {"banana", "laranja", "maca", "mamao", "melancia"}
ANO_ANALISE = 2025
MESES_PT = {
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


KEYWORDS = {
    "produto": ["produto", "produtos", "hortalica", "hortaliça", "fruta", "item", "mercadoria"],
    "ceasa": ["ceasa", "mercado", "entreposto", "unidade", "central", "atacadista"],
    "preco": ["preco", "preço", "medio", "médio", "r$/kg", "rs/kg", "valor", "cotacao", "cotação"],
    "quantidade": ["quantidade", "qtd", "volume", "oferta", "comercializada", "kg", "ton", "tonelada"],
    "categoria": ["categoria", "grupo", "classificacao", "classificação", "segmento"],
}


def listar_xlsx(raw_dir: str | Path) -> list[Path]:
    return sorted(Path(raw_dir).glob("*.xlsx"))


def identificar_colunas(colunas: list[object]) -> dict[str, list[str]]:
    nomes = [str(c) for c in colunas]
    resultado: dict[str, list[str]] = {}
    for alvo, palavras in KEYWORDS.items():
        encontrados = []
        for coluna in nomes:
            texto = normalizar_texto(coluna)
            if any(normalizar_texto(p) in texto for p in palavras):
                encontrados.append(coluna)
        resultado[alvo] = encontrados
    return resultado


def _melhor_coluna(colunas: list[str], termos_preferidos: list[str]) -> str | None:
    for termo in termos_preferidos:
        termo_norm = normalizar_texto(termo)
        for coluna in colunas:
            if termo_norm in normalizar_texto(coluna):
                return coluna
    return colunas[0] if colunas else None


def _encontrar_linha_cabecalho(df_raw: pd.DataFrame, limite: int = 20) -> int | None:
    melhor_linha = None
    melhor_pontos = 0
    limite = min(limite, len(df_raw))
    for idx in range(limite):
        valores = [normalizar_texto(v) for v in df_raw.iloc[idx].dropna().tolist()]
        texto = " ".join(valores)
        pontos = 0
        for palavras in KEYWORDS.values():
            if any(normalizar_texto(p) in texto for p in palavras):
                pontos += 1
        if pontos > melhor_pontos:
            melhor_pontos = pontos
            melhor_linha = idx
    return melhor_linha if melhor_pontos >= 2 else None


def _ler_aba_com_cabecalho(caminho: Path, aba: str) -> pd.DataFrame:
    bruto = pd.read_excel(caminho, sheet_name=aba, header=None, dtype=object)
    bruto = limpar_dataframe(bruto)
    if bruto.empty:
        return pd.DataFrame()
    linha_cabecalho = _encontrar_linha_cabecalho(bruto)
    if linha_cabecalho is None:
        df = pd.read_excel(caminho, sheet_name=aba, dtype=object)
        df = limpar_dataframe(df)
        df.columns = _deduplicar_colunas([nome_coluna(c) for c in df.columns])
        return df

    cabecalho = bruto.iloc[linha_cabecalho].fillna("").tolist()
    df = bruto.iloc[linha_cabecalho + 1 :].copy()
    df.columns = _deduplicar_colunas([nome_coluna(c) for c in cabecalho])
    return limpar_dataframe(df)


def _deduplicar_colunas(colunas: list[str]) -> list[str]:
    contagem: dict[str, int] = {}
    finais = []
    for coluna in colunas:
        base = coluna or "coluna"
        contagem[base] = contagem.get(base, 0) + 1
        finais.append(base if contagem[base] == 1 else f"{base}_{contagem[base]}")
    return finais


def diagnosticar_arquivo(caminho: Path) -> list[dict[str, object]]:
    diagnosticos = []
    xls = pd.ExcelFile(caminho)
    for aba in xls.sheet_names:
        try:
            previa = pd.read_excel(caminho, sheet_name=aba, header=None, nrows=8, dtype=object)
            df = _ler_aba_com_cabecalho(caminho, aba)
            diagnosticos.append(
                {
                    "arquivo": caminho.name,
                    "aba": aba,
                    "dimensoes": tuple(df.shape),
                    "colunas": [str(c) for c in df.columns],
                    "primeiras_linhas": previa.fillna("").astype(str).values.tolist(),
                    "possiveis_colunas": identificar_colunas(list(df.columns)),
                }
            )
        except Exception as exc:
            diagnosticos.append(
                {
                    "arquivo": caminho.name,
                    "aba": aba,
                    "erro": str(exc),
                    "dimensoes": (0, 0),
                    "colunas": [],
                    "primeiras_linhas": [],
                    "possiveis_colunas": {},
                }
            )
    return diagnosticos


def gerar_relatorio_diagnostico(raw_dir: str | Path, saida: str | Path) -> None:
    arquivos = listar_xlsx(raw_dir)
    linhas = [
        "# Diagnóstico das planilhas CONAB/Prohort 2025",
        "",
        "Relatório gerado automaticamente para apoiar a validação do parser.",
        "",
    ]
    if not arquivos:
        linhas += [
            "Nenhum arquivo XLSX foi encontrado em `data/raw/conab_prohort_2025/`.",
            "Inclua os arquivos reais e execute novamente o script de diagnóstico.",
            "",
        ]
    for arquivo in arquivos:
        linhas += [f"## {arquivo.name}", ""]
        for diag in diagnosticar_arquivo(arquivo):
            linhas += [f"### Aba: {diag['aba']}", ""]
            if diag.get("erro"):
                linhas += [f"- Erro de leitura: `{diag['erro']}`", ""]
                continue
            linhas += [
                f"- Dimensões interpretadas: `{diag['dimensoes'][0]} linhas x {diag['dimensoes'][1]} colunas`",
                f"- Colunas encontradas: `{', '.join(diag['colunas'])}`",
                "",
                "Possíveis colunas identificadas:",
            ]
            possiveis = diag.get("possiveis_colunas", {})
            rotulos = {"produto": "produto", "ceasa": "CEASA", "preco": "preço", "quantidade": "quantidade", "categoria": "categoria"}
            for chave in ["produto", "ceasa", "preco", "quantidade", "categoria"]:
                valores = possiveis.get(chave, []) if isinstance(possiveis, dict) else []
                linhas.append(f"- {rotulos[chave]}: {', '.join(valores) if valores else 'não identificado'}")
            linhas += ["", "Primeiras linhas da aba:", "", "| " + " | ".join([f"c{i+1}" for i in range(8)]) + " |", "| " + " | ".join(["---"] * 8) + " |"]
            for row in diag.get("primeiras_linhas", [])[:8]:
                row = (row + [""] * 8)[:8]
                linhas.append("| " + " | ".join(str(v).replace("|", "/")[:80] for v in row) + " |")
            linhas.append("")
    Path(saida).parent.mkdir(parents=True, exist_ok=True)
    Path(saida).write_text("\n".join(linhas), encoding="utf-8")


def extrair_arquivo(caminho: Path) -> pd.DataFrame:
    registros = []
    xls = pd.ExcelFile(caminho)
    for aba in xls.sheet_names:
        try:
            especifica = _extrair_aba_produto_especifico(caminho, aba)
            if not especifica.empty:
                registros.append(especifica)
                continue
            df = _ler_aba_com_cabecalho(caminho, aba)
            registros.append(_extrair_aba(df, caminho, aba))
        except Exception as exc:
            print(f"[AVISO] Não foi possível extrair {caminho.name} / {aba}: {exc}")
    if not registros:
        return pd.DataFrame(columns=COLUNAS_FINAIS)
    registros = [df for df in registros if not df.empty]
    if not registros:
        return pd.DataFrame(columns=COLUNAS_FINAIS)
    return finalizar_base(pd.concat(registros, ignore_index=True))


def _extrair_aba(df: pd.DataFrame, caminho: Path, aba: str) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=COLUNAS_FINAIS)
    colunas = [str(c) for c in df.columns]
    possiveis = identificar_colunas(colunas)
    produto_col = _melhor_coluna(possiveis["produto"], ["produto", "mercadoria", "item"])
    ceasa_col = _melhor_coluna(possiveis["ceasa"], ["ceasa", "mercado", "entreposto", "unidade"])
    preco_col = _melhor_coluna(possiveis["preco"], ["preco_medio", "preco", "r_kg", "valor"])
    quantidade_col = _melhor_coluna(possiveis["quantidade"], ["quantidade", "volume", "oferta", "kg", "ton"])
    categoria_col = _melhor_coluna(possiveis["categoria"], ["categoria", "grupo", "classificacao"])

    vitoria_cols = [c for c in colunas if eh_ceasa_es_vitoria(c)]
    if not ceasa_col and vitoria_cols:
        ceasa_col = None
        preco_vitoria = [c for c in vitoria_cols if any(t in normalizar_texto(c) for t in ["preco", "medio", "r_kg", "valor"])]
        qtd_vitoria = [c for c in vitoria_cols if any(t in normalizar_texto(c) for t in ["quant", "volume", "oferta", "kg", "ton"])]
        preco_col = preco_vitoria[0] if preco_vitoria else preco_col
        quantidade_col = qtd_vitoria[0] if qtd_vitoria else quantidade_col

    if not produto_col:
        return pd.DataFrame(columns=COLUNAS_FINAIS)

    base = remover_linhas_nao_dados(df, produto_col)
    if ceasa_col:
        base = base[base[ceasa_col].map(eh_ceasa_es_vitoria)]
    elif vitoria_cols:
        base = base.copy()
    else:
        # Algumas abas já podem ser específicas de Vitória; nesses casos, mantemos apenas quando o nome da aba indica isso.
        if not eh_ceasa_es_vitoria(aba):
            return pd.DataFrame(columns=COLUNAS_FINAIS)

    saida = pd.DataFrame()
    saida["ano"] = ano_por_nome_arquivo(caminho)
    saida["mes"] = mes_por_nome_arquivo(caminho)
    saida["ceasa"] = base[ceasa_col] if ceasa_col else "CEASA/ES - Vitória"
    saida["produto"] = base[produto_col]
    saida["categoria"] = base[categoria_col] if categoria_col else ""
    saida["preco_medio_kg"] = base[preco_col].map(numero_brasileiro) if preco_col else pd.NA
    saida["quantidade_kg"] = base[quantidade_col].map(numero_brasileiro) if quantidade_col else pd.NA
    saida["fonte_arquivo"] = caminho.name
    saida["fonte_aba"] = aba
    return finalizar_base(saida)


def consolidar_xlsx(raw_dir: str | Path) -> pd.DataFrame:
    frames = []
    for arquivo in listar_xlsx(raw_dir):
        try:
            parcial = extrair_arquivo(arquivo)
            if parcial.empty:
                print(f"[AVISO] Nenhum registro CEASA/ES - Vitória extraído de {arquivo.name}.")
            frames.append(parcial)
        except Exception as exc:
            print(f"[AVISO] Erro ao processar {arquivo.name}: {exc}")
    frames = [frame for frame in frames if not frame.empty]
    if not frames:
        return pd.DataFrame(columns=COLUNAS_FINAIS)
    df = finalizar_base(pd.concat(frames, ignore_index=True))
    if df.empty:
        return df
    agrupado = (
        df.groupby(["ano", "mes", "ceasa", "produto", "categoria"], dropna=False, as_index=False)
        .agg(
            preco_medio_kg=("preco_medio_kg", "mean"),
            quantidade_kg=("quantidade_kg", "mean"),
            fonte_arquivo=("fonte_arquivo", lambda s: "; ".join(sorted(set(map(str, s))))),
            fonte_aba=("fonte_aba", lambda s: "; ".join(sorted(set(map(str, s))))),
        )
    )
    return finalizar_base(agrupado)


def _produto_por_aba(aba: str) -> str | None:
    texto = normalizar_texto(aba).replace("precos-", "").replace("quantidade-", "")
    texto = texto.replace("precos_", "").replace("quantidade_", "").strip()
    texto = texto.replace("maca", "maca").replace("mamao", "mamao")
    if texto in HORTALICAS | FRUTAS:
        return texto
    return None


def _categoria_por_produto(produto: str) -> str:
    if produto in HORTALICAS:
        return "Hortaliças"
    if produto in FRUTAS:
        return "Frutas"
    return ""


def _extrair_aba_produto_especifico(caminho: Path, aba: str) -> pd.DataFrame:
    aba_norm = normalizar_texto(aba)
    if not (aba_norm.startswith("precos-") or aba_norm.startswith("precos_") or aba_norm.startswith("quantidade-") or aba_norm.startswith("quantidade_")):
        return pd.DataFrame(columns=COLUNAS_FINAIS)
    produto = _produto_por_aba(aba)
    if not produto:
        return pd.DataFrame(columns=COLUNAS_FINAIS)

    bruto = pd.read_excel(caminho, sheet_name=aba, header=None, dtype=object)
    if bruto.empty:
        return pd.DataFrame(columns=COLUNAS_FINAIS)

    header_idx = None
    for idx in range(min(8, len(bruto))):
        primeira_coluna = normalizar_texto(bruto.iloc[idx, 0])
        periodos = [_periodo_coluna(valor) for valor in bruto.iloc[idx, 1:].tolist()]
        tem_2025 = sum(1 for periodo in periodos if periodo and periodo[0] == ANO_ANALISE) >= 2
        if primeira_coluna == "ceasa" or tem_2025:
            header_idx = idx
            break
    if header_idx is None:
        return pd.DataFrame(columns=COLUNAS_FINAIS)

    linha_ceasa = None
    for idx in range(header_idx + 1, len(bruto)):
        if eh_ceasa_es_vitoria(bruto.iloc[idx, 0]):
            linha_ceasa = idx
            break
    if linha_ceasa is None:
        return pd.DataFrame(columns=COLUNAS_FINAIS)

    headers = bruto.iloc[header_idx].tolist()
    valores = bruto.iloc[linha_ceasa].tolist()
    is_preco = aba_norm.startswith("precos") or "preco" in normalizar_texto(bruto.iloc[2, 0] if len(bruto) > 2 else "")
    if is_preco and "2026" not in caminho.stem:
        return pd.DataFrame(columns=COLUNAS_FINAIS)
    registros = []
    for col_idx in range(1, len(headers)):
        header = headers[col_idx]
        valor = numero_brasileiro(valores[col_idx] if col_idx < len(valores) else None)
        if pd.isna(valor):
            continue
        periodo = _periodo_coluna(header)
        if not periodo or periodo[0] != ANO_ANALISE:
            continue
        ano, mes = periodo
        registros.append(
            {
                "ano": ano,
                "mes": mes,
                "ceasa": "CEASA/ES - Vitória",
                "produto": produto.upper(),
                "categoria": _categoria_por_produto(produto),
                "preco_medio_kg": valor if is_preco else pd.NA,
                "quantidade_kg": pd.NA if is_preco else valor,
                "fonte_arquivo": caminho.name,
                "fonte_aba": aba,
            }
        )
    if not registros:
        return pd.DataFrame(columns=COLUNAS_FINAIS)
    return finalizar_base(pd.DataFrame(registros))


def _periodo_coluna(valor: object) -> tuple[int, int] | None:
    data = pd.to_datetime(valor, errors="coerce")
    if pd.notna(data):
        return int(data.year), int(data.month)

    texto = normalizar_texto(valor)
    if not texto or "variacao" in texto or "/" in texto:
        return None
    ano_match = pd.Series([texto]).str.extract(r"(20\d{2})").iloc[0, 0]
    if pd.isna(ano_match):
        return None
    for mes_nome, mes_numero in MESES_PT.items():
        if normalizar_texto(mes_nome) in texto:
            return int(ano_match), mes_numero
    return None


def _escolher_coluna_periodo(candidatos: list[tuple[int, object, float]], ano: int, mes: int | None) -> tuple[int, object, float]:
    for candidato in candidatos:
        data = pd.to_datetime(candidato[1], errors="coerce")
        if pd.notna(data) and int(data.year) == int(ano) and (mes is None or int(data.month) == int(mes)):
            return candidato
    for candidato in reversed(candidatos):
        data = pd.to_datetime(candidato[1], errors="coerce")
        if pd.notna(data) and int(data.year) == int(ano):
            return candidato
    return candidatos[-1]
