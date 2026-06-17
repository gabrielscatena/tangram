# Tangram AI Feedback Lab

Mock **não produtivo**, porém organizado com práticas reais de engenharia, para demonstrar uma suíte de IA educacional voltada a correção discursiva, feedback formativo, human-in-the-loop, active learning, rastreabilidade e privacidade by design.

## Objetivo

Este pacote demonstra, de forma local e reproduzível, como poderia funcionar uma primeira versão de laboratório para a Tangram:

1. Receber uma resposta discursiva de estudante.
2. Pseudonimizar identificadores e mascarar PII no texto.
3. Pré-processar a resposta.
4. Recuperar rubricas e exemplos similares via busca semântica leve.
5. Classificar a resposta em rótulos pedagógicos.
6. Calcular score de ambiguidade/incerteza.
7. Gerar feedback formativo controlado.
8. Encaminhar casos ambíguos para revisão humana.
9. Registrar trace estruturado e métricas.
10. Alimentar ciclo de active learning.

## Stack

- Python 3.11
- Flask para UI/API
- DuckDB para persistência local analítica
- Scikit-learn para baseline leve
- Vector retrieval local via TF-IDF, com adaptação futura para Chroma/FAISS
- MLflow Tracking/Tracing opcional
- MkDocs Material + Mermaid para documentação
- Pytest para testes

## Quickstart com Conda

```bash
conda env create -f environment.yml
conda activate tangram-ai-feedback-lab

make init
make test
make run
```

Acesse:

- App: http://127.0.0.1:5000
- Docs: `make docs-serve`
- MLflow UI: `make mlflow-ui`

## Quickstart mínimo sem Flask/DuckDB/MLflow

O core foi construído para ser testável mesmo sem dependências opcionais:

```bash
python -m pytest tests/unit -q
python scripts/run_demo_pipeline.py
```

## Limites do mock

Este pacote **não** é uma implementação produtiva. Ele usa dados sintéticos, modelos simplificados e estratégias determinísticas para demonstrar arquitetura, fluxo e governança. Antes de uso real com estudantes, seriam necessários:

- Revisão jurídica e LGPD completa.
- Dados reais com consentimento e anonimização.
- Validação pedagógica formal.
- Avaliação de viés/fairness.
- Segurança, autenticação e controle de acesso.
- Observabilidade operacional robusta.
- Testes de carga, custo e latência.

## Estrutura

```text
tangram-ai-feedback-lab/
├── app/                    # Flask + camadas da aplicação
├── data/seed/              # Dados sintéticos
├── docs/                   # Documentação MkDocs/Mermaid
├── scripts/                # Scripts de inicialização e demo
├── tests/                  # Testes unitários e integração leve
├── environment.yml         # Ambiente Conda
├── pyproject.toml          # Qualidade de código
├── Makefile                # Comandos comuns
└── README.md
```

## BNCC, Bloom e Vector DB

A partir da v3, o mock inclui arquivos seed em `data/seed/` para alimentar o retriever/vector DB:

- `rubrics_bncc_bloom.csv` — rubricas avaliativas por questão.
- `bncc_financial_education_demo.csv` — recortes demonstrativos de alinhamento BNCC/educação financeira.
- `bloom_taxonomy.csv` — níveis da Taxonomia de Bloom e implicações para feedback.
- `financial_concepts.csv` — conceitos financeiros, misconceptions e dicas de feedback.

Rode `python scripts/build_vector_store.py` para gerar `data/vector_store/vector_index_manifest.json`. Os arquivos BNCC são demonstrativos e precisam ser substituídos/validados por material oficial antes de uso real.


## Pipeline com PDFs originais

Para criar o vector DB a partir de fontes oficiais em `data/raw/**/*.pdf`:

```bash
# 1) coloque os PDFs oficiais dentro de data/raw
# exemplo: copie o conteúdo de tangram_original_sources/data/raw para este projeto
cp -R ../tangram_original_sources/data/raw/* data/raw/

# 2) extraia texto por página, faça chunking versionado e construa o índice vetorial local
python scripts/build_raw_pdf_vector_db.py   --raw-dir data/raw   --processed-dir data/processed   --vector-dir data/vector_store   --chunk-size 900   --chunk-overlap 150   --pipeline-version raw_pdf_tfidf_v1.0

# 3) teste a recuperação semântica
python scripts/query_raw_vector_db.py "educação financeira consumo consciente" --top-k 5
```

Saídas principais:

```text
data/processed/source_pages.jsonl
data/processed/source_chunks.jsonl
data/vector_store/indexed_chunks.jsonl
data/vector_store/tfidf_vectorizer.joblib
data/vector_store/tfidf_matrix.npz
data/vector_store/vector_index_manifest.json
```

O manifesto registra hashes SHA256 dos PDFs originais e dos artefatos gerados.
