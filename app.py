from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.data_loader import carregar_dados
from src.insights import (
    gerar_insights_gerais,
    gerar_insights_modelos,
    gerar_insights_precos,
    gerar_insights_quantidade,
)
from src.metrics import (
    amplitude_preco,
    correlacao_preco_quantidade,
    extremos_mensais_por_produto,
    indice_mensal_por_produto,
    maior_alta_mensal,
    maior_queda_mensal,
    preco_medio_anual_produto,
    preco_medio_mensal,
    quantidade_total_produto,
    variacao_percentual_mensal,
    volatilidade_preco,
)
from src.models import aplicar_kmeans, detectar_variacoes_incomuns, interpretar_clusters, preparar_features_kmeans


st.set_page_config(page_title="CEASA-ES Hortifruti", layout="wide")


@st.cache_data
def load_data():
    return carregar_dados()


def moeda(valor: float | None) -> str:
    if pd.isna(valor):
        return "-"
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def numero(valor: float | None) -> str:
    if pd.isna(valor):
        return "-"
    return f"{valor:,.0f}".replace(",", ".")


MESES_NOMES = {
    1: "janeiro",
    2: "fevereiro",
    3: "março",
    4: "abril",
    5: "maio",
    6: "junho",
    7: "julho",
    8: "agosto",
    9: "setembro",
    10: "outubro",
    11: "novembro",
    12: "dezembro",
}


def nome_mes(valor: int | float | None) -> str:
    if pd.isna(valor):
        return "-"
    return MESES_NOMES.get(int(valor), str(valor))


df, ficticio, caminho = load_data()

st.title("Análise de hortifruti na CEASA-ES")
st.caption("MVP de apoio à análise de preços, oferta e sazonalidade com dados CONAB/Prohort filtrados para CEASA/ES - Vitória.")

if df.empty:
    st.warning(
        "Nenhum dado foi encontrado. Coloque os XLSX em data/raw/ e execute "
        "`python scripts/02_converter_xlsx_para_csv.py`."
    )
    st.stop()

if ficticio:
    st.warning(
        "O dashboard está usando um dataset fictício de exemplo em data/sample/. "
        "Ele existe apenas para permitir a execução técnica da aplicação e deve ser substituído pelos dados reais."
    )
else:
    st.info(f"Base carregada: {caminho}")

anos = sorted(df["ano"].dropna().astype(int).unique().tolist())
anos_sel = st.sidebar.multiselect("Ano", anos, default=anos)
if anos_sel:
    df = df[df["ano"].astype("Int64").isin(anos_sel)]

produtos = sorted(df["produto"].dropna().unique().tolist())
categorias = sorted([c for c in df["categoria"].dropna().unique().tolist() if str(c).strip()])
meses = sorted(df["mes"].dropna().astype(int).unique().tolist())

tab_geral, tab_precos, tab_qtd, tab_sazonalidade, tab_modelos, tab_impacto, tab_insights = st.tabs(
    [
        "Visão Geral",
        "Análise de Preços",
        "Quantidade / Oferta",
        "Sazonalidade",
        "Modelos Aplicados",
        "Impacto Social",
        "Insights",
    ]
)

with tab_geral:
    st.write(
        "A solução consolida dados CONAB/Prohort da CEASA/ES - Vitória para apoiar decisões de compra, "
        "venda, planejamento de oferta e acompanhamento de oscilações de preço."
    )
    vol = volatilidade_preco(df)
    top_vol = vol.sort_values("volatilidade_preco", ascending=False).head(1)
    top_preco = preco_medio_anual_produto(df).sort_values("preco_medio_anual", ascending=False).head(1)
    top_qtd = quantidade_total_produto(df).sort_values("quantidade_total_kg", ascending=False).head(1)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Registros", len(df))
    col2.metric("Produtos", df["produto"].nunique())
    col3.metric("Meses disponíveis", df["mes"].nunique())
    col4.metric("Preço médio geral", moeda(df["preco_medio_kg"].mean()))
    col5, col6, col7, col8 = st.columns(4)
    col5.metric("Quantidade total", numero(df["quantidade_kg"].sum()))
    col6.metric("Maior preço médio", top_preco.iloc[0]["produto"] if not top_preco.empty else "-")
    col7.metric("Maior volume", top_qtd.iloc[0]["produto"] if not top_qtd.empty else "-")
    col8.metric("Maior volatilidade", top_vol.iloc[0]["produto"] if not top_vol.empty else "-")
    st.plotly_chart(px.bar(quantidade_total_produto(df).head(20), x="produto", y="quantidade_total_kg", title="Quantidade total por produto"), use_container_width=True)

with tab_precos:
    col1, col2, col3 = st.columns(3)
    produtos_sel = col1.multiselect("Produto", produtos, default=produtos[: min(5, len(produtos))])
    meses_sel = col2.multiselect("Mês", meses, default=meses)
    categorias_sel = col3.multiselect("Categoria", categorias, default=categorias)
    filtro = df[df["produto"].isin(produtos_sel) & df["mes"].isin(meses_sel)]
    if categorias_sel:
        filtro = filtro[filtro["categoria"].isin(categorias_sel)]
    mensal = preco_medio_mensal(filtro)
    st.plotly_chart(px.line(mensal, x="mes", y="preco_medio_kg", color="produto", markers=True, title="Preço médio mensal por produto"), use_container_width=True)
    st.dataframe(variacao_percentual_mensal(filtro), use_container_width=True)
    col1, col2 = st.columns(2)
    col1.subheader("Ranking de maior preço médio anual")
    col1.dataframe(preco_medio_anual_produto(filtro).sort_values("preco_medio_anual", ascending=False), use_container_width=True)
    col2.subheader("Amplitude e volatilidade")
    risco = amplitude_preco(filtro).merge(volatilidade_preco(filtro), on="produto", how="outer")
    col2.dataframe(risco.sort_values("volatilidade_preco", ascending=False), use_container_width=True)
    col3, col4 = st.columns(2)
    col3.subheader("Maiores altas mensais")
    col3.dataframe(maior_alta_mensal(filtro), use_container_width=True)
    col4.subheader("Maiores quedas mensais")
    col4.dataframe(maior_queda_mensal(filtro), use_container_width=True)

with tab_qtd:
    total_prod = quantidade_total_produto(df).sort_values("quantidade_total_kg", ascending=False)
    st.plotly_chart(px.bar(total_prod.head(25), x="produto", y="quantidade_total_kg", title="Produtos mais comercializados"), use_container_width=True)
    qtd_mensal = df.dropna(subset=["quantidade_kg"]).groupby(["produto", "mes"], as_index=False)["quantidade_kg"].sum()
    produtos_qtd = st.multiselect("Produtos para linha de quantidade", produtos, default=produtos[: min(5, len(produtos))], key="prod_qtd")
    st.plotly_chart(px.line(qtd_mensal[qtd_mensal["produto"].isin(produtos_qtd)], x="mes", y="quantidade_kg", color="produto", markers=True, title="Quantidade mensal por produto"), use_container_width=True)
    dispersao = (
        df.groupby("produto", as_index=False)
        .agg(preco_medio=("preco_medio_kg", "mean"), quantidade_media=("quantidade_kg", "mean"))
        .dropna()
    )
    st.plotly_chart(px.scatter(dispersao, x="quantidade_media", y="preco_medio", text="produto", title="Comparação entre preço médio e quantidade"), use_container_width=True)
    corr = correlacao_preco_quantidade(df)
    st.caption(
        "A relação entre preço e quantidade é exploratória e não prova causalidade."
        + (f" Correlação observada na amostra: {corr:.2f}." if corr is not None else "")
    )

with tab_sazonalidade:
    st.write(
        "Esta seção mostra indícios de comportamento sazonal na série disponível. "
        "A interpretação deve considerar a cobertura de meses e anos presentes nas bases carregadas."
    )
    col1, col2 = st.columns(2)
    produtos_saz = col1.multiselect(
        "Produtos",
        produtos,
        default=produtos[: min(5, len(produtos))],
        key="produtos_sazonalidade",
    )
    categorias_saz = col2.multiselect(
        "Categorias",
        categorias,
        default=categorias,
        key="categorias_sazonalidade",
    )
    saz = df[df["produto"].isin(produtos_saz)]
    if categorias_saz:
        saz = saz[saz["categoria"].isin(categorias_saz)]

    indice = indice_mensal_por_produto(saz)
    extremos = extremos_mensais_por_produto(saz)

    st.subheader("Evolução mensal")
    col1, col2 = st.columns(2)
    col1.plotly_chart(
        px.line(
            indice,
            x="mes",
            y="preco_medio_kg",
            color="produto",
            markers=True,
            title="Preço médio por mês",
        ),
        use_container_width=True,
    )
    col2.plotly_chart(
        px.line(
            indice,
            x="mes",
            y="quantidade_kg",
            color="produto",
            markers=True,
            title="Quantidade por mês",
        ),
        use_container_width=True,
    )

    st.subheader("Meses de maior e menor valor")
    st.dataframe(extremos, use_container_width=True)

    if not indice.empty:
        pivot = indice.pivot_table(index="produto", columns="mes", values="indice_preco", aggfunc="mean")
        st.plotly_chart(
            px.imshow(
                pivot,
                aspect="auto",
                color_continuous_scale="RdYlGn_r",
                title="Índice mensal de preço por produto (média do produto = 100)",
            ),
            use_container_width=True,
        )
    st.caption(
        "Índices acima de 100 indicam meses em que o preço ficou acima da própria média anual; "
        "índices abaixo de 100 indicam meses abaixo da média anual."
    )

with tab_modelos:
    st.subheader("Modelo estatístico: detecção de variações incomuns")
    limite = st.slider("Limite percentual para ponto de atenção", min_value=10, max_value=60, value=20, step=5)
    alertas = detectar_variacoes_incomuns(df, limite)
    st.dataframe(alertas, use_container_width=True)
    if not alertas.empty:
        st.plotly_chart(px.bar(alertas.head(20), x="produto", y="variacao_percentual", color="tipo", title="Maiores oscilações relevantes"), use_container_width=True)
    st.write("Esta regra estatística marca pontos de atenção; ela não indica fraude, erro ou conclusão definitiva.")

    st.subheader("Modelo de aprendizado de máquina: K-Means")
    features = preparar_features_kmeans(df)
    if len(features) < 2:
        st.warning("Dados insuficientes para aplicar K-Means.")
        clusters = pd.DataFrame()
    else:
        max_k = min(4, len(features))
        k_default = 2 if len(features) < 6 else min(3, max_k)
        k = st.slider("Número de clusters", 2, max_k, k_default)
        clusters, score = aplicar_kmeans(features, k)
        if score is not None:
            st.metric("Silhouette score", f"{score:.2f}")
        st.plotly_chart(px.scatter(clusters, x="preco_medio_anual", y="volatilidade_preco", color="cluster", hover_name="produto", title="Agrupamento por preço médio e volatilidade"), use_container_width=True)
        st.dataframe(clusters, use_container_width=True)
        for cluster, texto in interpretar_clusters(clusters).items():
            st.write(f"Cluster {cluster}: {texto}")
        st.caption("O K-Means é um agrupamento exploratório não supervisionado e não gera classificação definitiva dos produtos.")

with tab_impacto:
    st.subheader("Impacto social e setorial")
    alertas_impacto = detectar_variacoes_incomuns(df, 20)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Anos analisados", df["ano"].nunique())
    col2.metric("Produtos monitorados", df["produto"].nunique())
    col3.metric("Pontos de atenção", len(alertas_impacto))
    col4.metric("Volume monitorado", numero(df["quantidade_kg"].sum()))

    st.subheader("KPIs de acompanhamento")
    kpis = pd.DataFrame(
        [
            {
                "kpi": "Cobertura da base",
                "valor": f"{df['ano'].nunique()} ano(s), {df['mes'].nunique()} mês(es), {df['produto'].nunique()} produto(s)",
                "uso": "Mede a amplitude da informação disponível para análise.",
            },
            {
                "kpi": "Produto de maior volume",
                "valor": quantidade_total_produto(df).sort_values("quantidade_total_kg", ascending=False).iloc[0]["produto"],
                "uso": "Indica item prioritário para gestão de abastecimento.",
            },
            {
                "kpi": "Produto de maior volatilidade",
                "valor": volatilidade_preco(df).sort_values("volatilidade_preco", ascending=False).iloc[0]["produto"],
                "uso": "Ajuda a identificar produtos que exigem maior acompanhamento de preço.",
            },
            {
                "kpi": "Correlação preço x quantidade",
                "valor": f"{correlacao_preco_quantidade(df):.2f}" if correlacao_preco_quantidade(df) is not None else "indisponível",
                "uso": "Apoia a leitura da relação entre oferta comercializada e preço médio.",
            },
        ]
    )
    st.dataframe(kpis, use_container_width=True)

    mensal_impacto = (
        df.groupby(["produto", "mes"], as_index=False)
        .agg(preco_medio_kg=("preco_medio_kg", "mean"), quantidade_kg=("quantidade_kg", "mean"))
        .dropna(subset=["produto", "mes"])
    )
    recomendacoes = []
    for produto, grupo in mensal_impacto.groupby("produto"):
        preco = grupo.dropna(subset=["preco_medio_kg"])
        quantidade = grupo.dropna(subset=["quantidade_kg"])
        if preco.empty or quantidade.empty:
            continue
        melhor_preco = preco.loc[preco["preco_medio_kg"].idxmin()]
        maior_oferta = quantidade.loc[quantidade["quantidade_kg"].idxmax()]
        recomendacoes.append(
            {
                "produto": produto,
                "janela_de_compra": nome_mes(melhor_preco["mes"]),
                "preco_medio_kg": melhor_preco["preco_medio_kg"],
                "mes_maior_oferta": nome_mes(maior_oferta["mes"]),
                "quantidade_media_kg": maior_oferta["quantidade_kg"],
                "acao_sugerida": (
                    f"Deve-se considerar reforçar compras em {nome_mes(melhor_preco['mes'])}, "
                    f"quando o preço médio observado foi mais competitivo; negociar estoque e oferta com atenção em "
                    f"{nome_mes(maior_oferta['mes'])}, mês de maior volume médio."
                ),
            }
        )
    recomendacoes_df = pd.DataFrame(recomendacoes)
    if not recomendacoes_df.empty:
        recomendacoes_df = recomendacoes_df.merge(quantidade_total_produto(df), on="produto", how="left")
        recomendacoes_df = recomendacoes_df.sort_values("quantidade_total_kg", ascending=False)

    st.subheader("Recomendações para negociação")
    st.dataframe(
        recomendacoes_df[
            [
                "produto",
                "janela_de_compra",
                "preco_medio_kg",
                "mes_maior_oferta",
                "quantidade_media_kg",
                "acao_sugerida",
            ]
        ],
        use_container_width=True,
    )

    volume_total = quantidade_total_produto(df).sort_values("quantidade_total_kg", ascending=False)
    preco_anual = preco_medio_anual_produto(df).sort_values("preco_medio_anual")
    vol_preco = volatilidade_preco(df).sort_values("volatilidade_preco", ascending=False)
    produto_volume = volume_total.iloc[0]
    produto_barato = preco_anual.iloc[0]
    produto_risco = vol_preco.iloc[0]

    st.subheader("Conclusões aplicadas")
    st.write(
        f"- Deve-se tratar {produto_volume['produto']} como item estratégico de abastecimento, pois concentrou "
        f"{numero(produto_volume['quantidade_total_kg'])} kg na série filtrada.\n"
        f"- Para reduzir custo de compra, deve-se priorizar negociações nos meses indicados na tabela acima, "
        f"quando cada produto apresentou menor preço médio por kg.\n"
        f"- {produto_barato['produto']} apresentou o menor preço médio geral da base filtrada "
        f"({moeda(produto_barato['preco_medio_anual'])}/kg), sendo opção relevante para estratégias de oferta com menor preço ao consumidor.\n"
        f"- {produto_risco['produto']} exige acompanhamento mais frequente, pois teve a maior volatilidade de preço; "
        "para esse tipo de produto, o negociante deve evitar compras grandes sem comparar o histórico recente.\n"
        "- As recomendações são apoio à decisão: clima, safra, transporte e demanda local ainda precisam ser avaliados antes de fechar compras ou contratos."
    )

with tab_insights:
    alertas = detectar_variacoes_incomuns(df, 20)
    features = preparar_features_kmeans(df)
    clusters, _ = aplicar_kmeans(features, 2 if len(features) < 6 else min(3, len(features))) if len(features) >= 2 else (pd.DataFrame(), None)
    todos = (
        gerar_insights_gerais(df)
        + gerar_insights_precos(df)
        + gerar_insights_quantidade(df)
        + gerar_insights_modelos(alertas, clusters)
    )
    for item in todos:
        st.write(f"- {item}")
