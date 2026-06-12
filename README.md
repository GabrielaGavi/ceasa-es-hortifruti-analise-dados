# Análise de preços de hortifruti na CEASA-ES

## Tema

Análise de preços, oferta e comportamento sazonal de hortifruti na CEASA-ES, com foco nos dados CONAB/Prohort filtrados para CEASA/ES - Vitória. Grupo: Gabriela Gave Gavi, Jeronymo Francisco Moreira Neto, José Luiz dos Santos Azeredo Mendes, Pedro Henrique Bispo Sarmento, Pedro Henrique Ferreira Bonela.

- Vídeo demonstração MVP final (entrega 3) - https://youtu.be/6zu6yjah3J0


## Sociedade impactada

O projeto atende produtores rurais, comerciantes, atacadistas, permissionários, compradores de mercados, restaurantes e feiras, consumidores finais e gestores públicos interessados em abastecimento alimentar.

## Objetivo da Entrega 3

Esta entrega apresenta um MVP final para apoiar a leitura de preços, oferta e sazonalidade de produtos hortifrutigranjeiros comercializados na CEASA/ES - Vitória. O objetivo é transformar arquivos XLSX públicos da CONAB/Prohort em bases CSV padronizadas, disponibilizar um dashboard interativo, aplicar modelos estatísticos e de aprendizado de máquina e registrar conclusões úteis para tomada de decisão no setor de abastecimento.

## Fonte dos dados

A base principal utiliza os arquivos XLSX da CONAB/Prohort baixados manualmente pelo grupo. O arquivo de janeiro de 2026 é usado como fonte principal de preços, pois contém a série de preços de 2025 nas abas por produto. Os boletins mensais de 2025 complementam a série de quantidade por produto. Também foram incluídos boletins de 2024 para ampliar a comparação histórica disponível no MVP.

Os arquivos devem ficar em:

```text
data/raw/conab_prohort_2025/
data/raw/conab_prohort_2024/
```

Arquivo principal esperado:

```text
janeiro_2026_base_2025.xlsx
```

Também podem ser usados os boletins mensais de 2025 para complementar as quantidades:

```text
fevereiro_2025.xlsx
marco_2025.xlsx
abril_2025.xlsx
...
dezembro_2025.xlsx
```

O parser tenta identificar colunas de CEASA, produto, categoria, preço médio, quantidade e volume, mesmo quando os nomes variam entre abas.

## Conversão para CSV

O script de conversão lê os XLSX, prioriza registros da CEASA/ES - Vitória e gera arquivos padronizados em `data/processed/`.

```text
data/processed/conab_prohort_2025_ceasa_es.csv
data/processed/conab_prohort_2024_ceasa_es.csv
```

Estrutura padrão:

```text
ano,mes,ceasa,produto,categoria,preco_medio_kg,quantidade_kg,fonte_arquivo,fonte_aba
```

O dashboard carrega automaticamente os arquivos processados que seguem o padrão `data/processed/conab_prohort_*_ceasa_es.csv`. Se não houver XLSX na pasta `raw`, o script cria um dataset fictício em `data/sample/dados_exemplo_conab_prohort_2025.csv` apenas para permitir a execução técnica da aplicação. Esse arquivo não representa dados reais e deve ser substituído pelos dados oficiais.

## Tecnologias

- Python
- Pandas
- NumPy
- OpenPyXL
- Streamlit
- Plotly
- Scikit-learn
- Git/GitHub

## Instalação

```bash
pip install -r requirements.txt
```

## Diagnóstico das planilhas

```bash
python scripts/01_diagnosticar_planilhas.py
```

O relatório será salvo em:

```text
docs/diagnostico_planilhas.md
```

## Conversão dos XLSX

```bash
python scripts/02_converter_xlsx_para_csv.py
```

Para converter outro ano/diretório no mesmo padrão:

```bash
python scripts/02_converter_xlsx_para_csv.py --raw-dir data/raw/conab_prohort_2024 --saida data/processed/conab_prohort_2024_ceasa_es.csv --ano 2024
```

## Execução do Streamlit

```bash
python -m streamlit run app.py
```

A aplicação carrega todas as bases processadas disponíveis em `data/processed/` e permite filtrar a análise por ano no menu lateral.

## Estrutura

```text
projeto-analise-dados-ceasa-hortifruti/
|-- app.py
|-- requirements.txt
|-- README.md
|-- data/
|   |-- raw/
|   |   |-- conab_prohort_2024/
|   |   `-- conab_prohort_2025/
|   |-- processed/
|   `-- sample/
|-- src/
|   |-- conab_parser.py
|   |-- data_loader.py
|   |-- preprocessing.py
|   |-- metrics.py
|   |-- models.py
|   `-- insights.py
|-- scripts/
|   |-- 01_diagnosticar_planilhas.py
|   `-- 02_converter_xlsx_para_csv.py
`-- 
```

## Métricas calculadas

- Preço médio mensal
- Preço médio anual por produto
- Quantidade total por produto
- Quantidade média mensal por produto
- Variação percentual mês a mês
- Indícios de sazonalidade por mês
- Mês de maior e menor preço por produto
- Mês de maior e menor quantidade por produto
- Amplitude de preço
- Volatilidade do preço
- Maior alta mensal
- Maior queda mensal
- Correlação exploratória entre preço médio e quantidade comercializada, quando houver dados suficientes

## Modelos aplicados

1. Detecção estatística de variações incomuns: regra baseada na variação percentual mensal por produto.
2. K-Means: modelo de aprendizado de máquina não supervisionado para agrupamento exploratório de produtos por comportamento de preço, volatilidade e quantidade.

## Impacto social

O projeto impacta a cadeia de abastecimento alimentar ao transformar boletins públicos em indicadores acessíveis para agentes que precisam tomar decisões rápidas e baseadas em dados. A solução atende produtores rurais, atacadistas, permissionários, compradores de supermercados, restaurantes, feirantes, consumidores e gestores públicos interessados no acompanhamento do abastecimento da CEASA-ES.

Principais formas de impacto:

- Apoio ao planejamento de compra e venda por meio da visualização de preços médios, volumes comercializados e oscilações mensais.
- Identificação de produtos com maior volatilidade, permitindo acompanhamento preventivo de itens mais sensíveis a variações de mercado.
- Transparência sobre o comportamento de oferta e preço de produtos relevantes para alimentação cotidiana.
- Redução do esforço manual de leitura de múltiplas planilhas mensais da CONAB/Prohort.
- Apoio à gestão pública e setorial com indicadores que ajudam a observar pressões de abastecimento e sazonalidade.

## KPIs de acompanhamento

- Cobertura temporal: quantidade de anos e meses disponíveis nas bases processadas.
- Produtos monitorados: número de produtos com série de preço e quantidade.
- Preço médio geral: média do preço por kg dos produtos filtrados.
- Volume total monitorado: soma da quantidade comercializada em kg.
- Produto de maior volume: item com maior quantidade comercializada no período analisado.
- Produto de maior volatilidade: item com maior desvio padrão de preço na série.
- Pontos de atenção: quantidade de variações mensais acima do limite percentual definido no dashboard.
- Correlação preço x quantidade: indicador exploratório da relação entre preço médio e volume comercializado.

## Conclusões

A consolidação dos dados de 2024 e 2025 aumenta a capacidade de comparar períodos, observar tendências e identificar produtos que exigem maior atenção. Na base processada atual, batata, laranja e banana aparecem como produtos de alto impacto operacional por concentrarem os maiores volumes comercializados. Para o negociante da CEASA-ES, esses itens devem ser acompanhados com prioridade, pois pequenas variações de preço ou oferta podem representar impacto relevante no abastecimento e no custo final.

Conclusões aplicadas para compra, venda e planejamento:

- Deve-se tratar a batata como produto estratégico de abastecimento, pois ela concentra o maior volume total da base processada. Na série analisada, a menor média mensal de preço da batata aparece em dezembro, que também é o mês de maior oferta média disponível; isso indica uma janela favorável para negociação, recomposição de estoque e compra em maior escala, sempre validando a safra e a demanda do momento.
- Deve-se acompanhar cenoura, cebola e batata com maior frequência, pois são os produtos com maior volatilidade de preço na série. Para esses itens, compras grandes devem ser feitas com mais cautela e, quando possível, com comparação do histórico recente.
- Para produtos com menor preço médio geral, como melancia, cebola, laranja e banana, o setor pode explorar estratégias comerciais voltadas a maior giro, promoções e abastecimento regular, pois tendem a ser itens mais competitivos no preço por kg.
- Para itens de preço médio mais alto, como maçã e mamão, o negociante deve observar melhor o momento de compra e evitar formar estoque em meses de pico de preço, pois a margem pode ser mais sensível.
- Os meses de maior oferta média ajudam a orientar planejamento logístico: banana e maçã se destacam em agosto; tomate, alface e mamão em julho; laranja, cebola e melancia em períodos próximos ao segundo semestre; batata aparece mais forte em dezembro na base disponível.

Janelas observadas na base atual:

| Produto | Melhor mês médio para compra por preço | Mês de maior oferta média | Leitura para o setor |
| --- | --- | --- | --- |
| ALFACE | Outubro | Julho | Comprar com mais atenção em outubro e planejar oferta forte em julho. |
| BANANA | Outubro | Agosto | Produto de alto volume; agosto favorece abastecimento e outubro favorece preço. |
| BATATA | Dezembro | Dezembro | Produto âncora; dezembro aparece como janela favorável para volume e preço. |
| CEBOLA | Outubro | Agosto | Alta volatilidade; outubro favorece preço e agosto favorece disponibilidade. |
| CENOURA | Agosto | Maio | Produto volátil; comprar com disciplina de preço e atenção à oferta de maio. |
| LARANJA | Dezembro | Outubro | Boa opção de giro; outubro indica maior oferta e dezembro melhor preço médio. |
| MAÇÃ | Abril | Agosto | Item de preço mais alto; abril favorece compra e agosto favorece disponibilidade. |
| MAMÃO | Outubro | Julho | Produto sensível a preço; julho favorece oferta e outubro favorece compra. |
| MELANCIA | Outubro | Dezembro | Menor preço médio geral; útil para estratégia de volume e preço competitivo. |
| TOMATE | Novembro | Julho | Produto relevante e volátil; julho favorece oferta e novembro favorece compra. |

As conclusões devem ser interpretadas como apoio à decisão, não como prova causal definitiva. Fatores externos como clima, transporte, safra, demanda regional e custos logísticos também influenciam os preços e devem ser considerados antes de fechar compras, contratos ou políticas de abastecimento.

