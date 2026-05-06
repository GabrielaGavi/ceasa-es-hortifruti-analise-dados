# Análise de preços de hortifruti na CEASA-ES

## Tema

Análise de preços e procedência de hortifrúti na CEASA-ES, com foco nos dados CONAB/Prohort de 2025 filtrados para CEASA/ES - Vitória. Grupo: Gabriela Gave Gavi, Jeronymo Francisco Moreira Neto, José Luiz dos Santos Azeredo Mendes, Pedro Henrique Bispo Sarmento, Pedro Henrique Ferreira Bonela.

- Vídeo demonstração protótipo (entrega 2) - https://youtu.be/oIwFn-vIlMM


## Sociedade impactada

O projeto atende produtores rurais, comerciantes, atacadistas, permissionários, compradores de mercados, restaurantes e feiras, consumidores finais e gestores públicos interessados em abastecimento alimentar.

## Objetivo da Entrega 2

Esta entrega apresenta um protótipo preliminar, ainda não caracterizado como MVP final. O objetivo é demonstrar a viabilidade da análise de dados, a transformação dos arquivos XLSX em uma base consolidada CSV, a aplicação inicial de modelos e a geração de primeiros insights.

## Fonte dos dados

A base principal utiliza os arquivos XLSX da CONAB/Prohort baixados manualmente pelo grupo. O arquivo de janeiro de 2026 é usado como fonte principal de preços, pois contém a série de preços de 2025 nas abas por produto. Os boletins mensais de 2025 complementam a série de quantidade por produto.

Os arquivos devem ficar em:

```text
data/raw/conab_prohort_2025/
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

O script de conversão lê os XLSX, prioriza registros da CEASA/ES - Vitória e gera:

```text
data/processed/conab_prohort_2025_ceasa_es.csv
```

Estrutura padrão:

```text
ano,mes,ceasa,produto,categoria,preco_medio_kg,quantidade_kg,fonte_arquivo,fonte_aba
```

Se não houver XLSX na pasta `raw`, o script cria um dataset fictício em `data/sample/dados_exemplo_conab_prohort_2025.csv` apenas para permitir a demonstração do dashboard. Esse arquivo não representa dados reais e deve ser substituído pelos dados oficiais.

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

## Execução do Streamlit

```bash
python -m streamlit run app.py
```

## Estrutura

```text
projeto-analise-dados-ceasa-hortifruti/
|-- app.py
|-- requirements.txt
|-- README.md
|-- data/
|   |-- raw/
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
- Correlação preliminar entre preço médio e quantidade comercializada, quando houver dados suficientes

## Modelos aplicados

1. Detecção estatística de variações incomuns: regra preliminar baseada na variação percentual mensal por produto.
2. K-Means: modelo de aprendizado de máquina não supervisionado para agrupamento preliminar de produtos por comportamento de preço, volatilidade e quantidade.
