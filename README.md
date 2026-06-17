# Tangram AI Feedback Lab

Mock técnico **não produtivo**, porém estruturado com práticas reais de engenharia de software, MLOps, rastreabilidade, governança de IA e privacidade by design.

O projeto demonstra uma suíte experimental de IA educacional para correção discursiva, feedback formativo, recuperação de contexto em fontes oficiais, human-in-the-loop, active learning e observabilidade.

> **Status atual:** laboratório técnico local para demonstração de arquitetura.
> **Não usar em produção com estudantes reais sem validação pedagógica, jurídica, LGPD, segurança e avaliação formal.**

---

## 1. Objetivo

O Tangram AI Feedback Lab demonstra, de forma local e reproduzível, como poderia funcionar uma primeira versão de laboratório para a plataforma Tangram:

1. Carregar um banco de questões discursivas de educação financeira.
2. Permitir que o estudante selecione uma questão e envie uma resposta.
3. Pseudonimizar identificadores do estudante.
4. Mascarar possíveis informações pessoais no texto da resposta.
5. Pré-processar a resposta discursiva.
6. Montar uma query contextual com:

   * enunciado da questão;
   * resposta do estudante;
   * tópico financeiro;
   * nível de dificuldade;
   * nível Bloom;
   * habilidade BNCC demonstrativa;
   * resposta esperada;
   * rubricas.
7. Recuperar trechos relevantes de documentos oficiais usando um vector DB local.
8. Classificar a resposta em rótulos pedagógicos iniciais.
9. Calcular um score de ambiguidade/incerteza.
10. Gerar feedback formativo controlado.
11. Encaminhar casos ambíguos para revisão humana.
12. Persistir trace estruturado da avaliação.
13. Expor APIs para questões, avaliação, busca vetorial e traces.
14. Alimentar um ciclo demonstrativo de active learning.

---

## 2. Escopo do MVP técnico

Este projeto busca demonstrar o seguinte fluxo ponta a ponta:

```text
question_bank.csv
  -> seleção da questão na UI
  -> resposta discursiva do estudante
  -> pseudonimização e privacy preprocessing
  -> RAG em fontes oficiais
  -> classificação pedagógica inicial
  -> score de ambiguidade
  -> feedback formativo controlado
  -> human review quando necessário
  -> trace estruturado e auditável
```

O MVP técnico é considerado pronto quando os seguintes itens funcionam:

| Critério                   | Validação esperada                                                   |
| -------------------------- | -------------------------------------------------------------------- |
| Dropdown com questões      | `/student` lista as 50 questões do `question_bank.csv`               |
| Fontes originais indexadas | `vector_index_manifest.json` mostra PDFs, hashes e chunks            |
| Vector DB ativo            | backend `raw_pdf_tfidf_vector_store`                                 |
| RAG funcional              | `/api/vector-search` retorna trechos com documento, página e preview |
| Avaliação funcional        | `/api/evaluate` retorna feedback e `trace_id`                        |
| Trace auditável            | `/api/traces/<trace_id>` mostra etapas do processamento              |
| Human-in-the-loop          | respostas ambíguas entram em revisão                                 |
| Persistência local         | traces e respostas são gravados localmente                           |
| Testes/checker             | `check_mvp_technical.py` passa sem falhas críticas                   |

---

## 3. O que este projeto NÃO é

Este projeto **não** é uma solução produtiva pronta.

Ele ainda não substitui:

* validação pedagógica por especialistas;
* rubricas oficiais finais;
* avaliação humana formal;
* modelo treinado com respostas reais de estudantes;
* autenticação e autorização;
* governança LGPD completa;
* infraestrutura escalável;
* banco transacional produtivo;
* vector DB produtivo;
* validação de viés/fairness;
* deploy seguro;
* observabilidade operacional completa.

---

## 4. Stack

| Camada             | Tecnologia                         |
| ------------------ | ---------------------------------- |
| Linguagem          | Python 3.11                        |
| UI/API             | Flask                              |
| Persistência local | DuckDB e/ou JSONL estruturado      |
| Retrieval          | TF-IDF local com scikit-learn      |
| Vector artifacts   | `joblib`, `scipy.sparse`, JSONL    |
| Baseline ML        | scikit-learn                       |
| Tracing local      | JSONL estruturado                  |
| MLOps opcional     | MLflow Tracking/Tracing            |
| Documentação       | Markdown, MkDocs Material, Mermaid |
| Testes             | Pytest                             |
| Execução local     | Conda / PowerShell / Bash          |

---

## 5. Estrutura do projeto

```text
tangram-ai-feedback-lab/
├── app/
│   ├── application/              # Use cases da aplicação
│   ├── domain/                   # Entidades e contratos de domínio
│   ├── infrastructure/           # Adapters de persistência, retrieval, tracing
│   ├── routes/                   # Blueprints Flask
│   ├── templates/                # Páginas HTML
│   └── static/                   # CSS/JS/assets
│
├── data/
│   ├── raw/                      # PDFs originais públicos/oficiais
│   │   ├── bcb/
│   │   ├── bncc/
│   │   ├── mec_tct/
│   │   └── bloom_reference/
│   │
│   ├── seed/                     # Dados demonstrativos
│   │   └── question_bank.csv
│   │
│   ├── processed/                # Páginas e chunks extraídos dos PDFs
│   │   ├── source_pages.jsonl
│   │   └── source_chunks.jsonl
│   │
│   └── vector_store/             # Artefatos do vector DB local
│       ├── tfidf_vectorizer.joblib
│       ├── tfidf_matrix.npz
│       ├── indexed_chunks.jsonl
│       └── vector_index_manifest.json
│
├── docs/                         # Documentação técnica/pedagógica
├── scripts/                      # Scripts operacionais e de validação
├── tests/                        # Testes unitários e integração leve
├── environment.yml               # Ambiente Conda
├── requirements.txt              # Dependências pip
├── pyproject.toml                # Configuração de qualidade de código
├── Makefile                      # Comandos comuns em Unix-like
└── README.md
```

---

## 6. Dados e fontes originais

O projeto inclui documentos públicos/oficiais para substituir recortes sintéticos usados nas primeiras versões do mock.

### 6.1 Arquivos em `data/raw`

| Arquivo                                                                | Descrição                                                                         |
| ---------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| `data/raw/bncc/BNCC_20dez_site.pdf`                                    | BNCC completa, PDF oficial do MEC/BNCC                                            |
| `data/raw/mec_tct/caderno_economia_consolidado_v_final_09_03_2022.pdf` | Caderno Economia dos Temas Contemporâneos Transversais da BNCC                    |
| `data/raw/mec_tct/contextualizacao_temas_contemporaneos.pdf`           | Documento de contextualização dos TCTs na BNCC                                    |
| `data/raw/mec_tct/guia_pratico_temas_contemporaneos.pdf`               | Guia prático dos TCTs                                                             |
| `data/raw/bcb/Matriz_Geral_Letramento_Financeiro.pdf`                  | Matriz de Competências de Letramento Financeiro do Banco Central / Aprender Valor |
| `data/raw/bcb/art8_educacao_financeira_escolas.pdf`                    | Artigo do Banco Central sobre educação financeira nas escolas                     |
| `data/raw/bloom_reference/bloom_sources_manifest.json`                 | Manifesto com referências de Bloom/Krathwohl                                      |

### 6.2 Observação sobre Bloom

A Taxonomia de Bloom e a revisão de Krathwohl são obras acadêmicas protegidas por direitos autorais.

Por isso, este projeto **não redistribui PDFs completos protegidos** de Bloom/Krathwohl. O projeto inclui apenas referências e metadados em:

```text
data/raw/bloom_reference/bloom_sources_manifest.json
```

Para um produto real, recomenda-se:

1. usar fontes públicas/oficiais com licença adequada;
2. produzir resumos próprios com equipe pedagógica;
3. manter referências bibliográficas;
4. não indexar texto integral protegido sem autorização.

---

## 7. Banco de questões

O arquivo principal de questões é:

```text
data/seed/question_bank.csv
```

Ele contém 50 questões discursivas demonstrativas de educação financeira.

### 7.1 Colunas esperadas

```csv
question_id,title,prompt,grade_level,financial_topic,bncc_area,bncc_skill,bloom_level,difficulty,expected_answer,rubric_conceptual,rubric_clarity,rubric_structure
```

### 7.2 Níveis de dificuldade

| Valor     | Descrição                                           |
| --------- | --------------------------------------------------- |
| `facil`   | Questões conceituais simples                        |
| `medio`   | Questões de aplicação, comparação e análise inicial |
| `dificil` | Questões que exigem análise, avaliação ou criação   |

### 7.3 Observação sobre BNCC

Os campos `bncc_skill` atualmente usam identificadores demonstrativos, por exemplo:

```text
BNCC_DEMO_EF_MAT_EDFIN_JUROS_02
```

Esses códigos **não são códigos oficiais da BNCC**. Para produção, devem ser substituídos por códigos oficiais validados por equipe pedagógica.

---

## 8. Pipeline de fontes originais para vector DB

O pipeline de indexação converte PDFs originais em chunks pesquisáveis.

```text
data/raw/**/*.pdf
  -> extração de texto por página
  -> data/processed/source_pages.jsonl
  -> chunking versionado com overlap
  -> data/processed/source_chunks.jsonl
  -> TF-IDF embeddings
  -> data/vector_store/tfidf_vectorizer.joblib
  -> data/vector_store/tfidf_matrix.npz
  -> data/vector_store/indexed_chunks.jsonl
  -> data/vector_store/vector_index_manifest.json
```

### 8.1 Gerar o vector DB

No Windows PowerShell:

```powershell
python .\scripts\build_raw_pdf_vector_db.py `
  --raw-dir .\data\raw `
  --processed-dir .\data\processed `
  --vector-dir .\data\vector_store `
  --chunk-size 900 `
  --chunk-overlap 150 `
  --pipeline-version raw_pdf_tfidf_v1.0
```

Em Bash:

```bash
python scripts/build_raw_pdf_vector_db.py \
  --raw-dir data/raw \
  --processed-dir data/processed \
  --vector-dir data/vector_store \
  --chunk-size 900 \
  --chunk-overlap 150 \
  --pipeline-version raw_pdf_tfidf_v1.0
```

### 8.2 Validar manifesto

```powershell
python -m json.tool .\data\vector_store\vector_index_manifest.json
```

O manifesto deve conter:

```json
{
  "pipeline_version": "raw_pdf_tfidf_v1.0",
  "counts": {
    "source_files": 6,
    "chunks": 1677
  },
  "vector_index": {
    "backend": "tfidf_local_vector_store",
    "matrix_shape": [1677, 50000]
  }
}
```

Os números podem variar se os documentos, chunk size ou dependências forem alterados.

---

## 9. Quickstart com Conda

### 9.1 Criar ambiente

```bash
conda env create -f environment.yml
conda activate tangram-ai-feedback-lab
```

Ou, se o ambiente já existir:

```bash
conda activate tangram-ai-feedback-lab
pip install -r requirements.txt
```

### 9.2 Inicializar dados locais

```bash
python scripts/init_db.py
python scripts/seed_data.py
```

### 9.3 Criar vector DB a partir dos PDFs

```bash
python scripts/build_raw_pdf_vector_db.py \
  --raw-dir data/raw \
  --processed-dir data/processed \
  --vector-dir data/vector_store \
  --chunk-size 900 \
  --chunk-overlap 150 \
  --pipeline-version raw_pdf_tfidf_v1.0
```

### 9.4 Rodar testes

```bash
python -m pytest tests -q
```

### 9.5 Rodar aplicação

```bash
python -m flask --app app run --host 127.0.0.1 --port 5000 --no-reload
```

Acesse:

```text
http://127.0.0.1:5000
```

Tela principal do estudante:

```text
http://127.0.0.1:5000/student
```

---

## 10. Quickstart no Windows PowerShell

Na raiz do projeto:

```powershell
cd C:\Users\gabri\Documents\tangram-ai-feedback-lab\tangram-ai-feedback-lab
conda activate tangram-ai-feedback-lab
```

Instale dependências:

```powershell
pip install -r requirements.txt
```

Inicialize dados:

```powershell
python .\scripts\init_db.py
python .\scripts\seed_data.py
```

Gere o vector DB:

```powershell
python .\scripts\build_raw_pdf_vector_db.py --raw-dir .\data\raw --processed-dir .\data\processed --vector-dir .\data\vector_store --chunk-size 900 --chunk-overlap 150 --pipeline-version raw_pdf_tfidf_v1.0
```

Rode Flask sem reloader:

```powershell
$env:FLASK_DEBUG="0"
python -m flask --app app run --host 127.0.0.1 --port 5000 --no-reload
```

Em outro terminal, teste:

```powershell
Invoke-RestMethod http://127.0.0.1:5000/api/questions
```

---

## 11. Rotas da aplicação

Para listar as rotas registradas:

```powershell
python -m flask --app app routes
```

Rotas esperadas:

| Endpoint                                | Métodos   | Rota                               |
| --------------------------------------- | --------- | ---------------------------------- |
| `student.index`                         | GET       | `/`                                |
| `student.student_playground`            | GET, POST | `/student`                         |
| `api.list_questions`                    | GET       | `/api/questions`                   |
| `api.evaluate_response`                 | POST      | `/api/evaluate`                    |
| `api.vector_search`                     | GET, POST | `/api/vector-search`               |
| `observability.observability_dashboard` | GET       | `/observability`                   |
| `observability.trace_detail`            | GET       | `/observability/traces/<trace_id>` |
| `observability.trace_detail_api`        | GET       | `/api/traces/<trace_id>`           |
| `teacher.teacher_review`                | GET       | `/teacher/review`                  |
| `annotation.annotation_studio`          | GET, POST | `/annotation`                      |
| `rubric.rubric_manager`                 | GET       | `/rubrics`                         |

---

## 12. APIs principais

### 12.1 Listar questões

```powershell
Invoke-RestMethod http://127.0.0.1:5000/api/questions
```

Resposta esperada:

```json
{
  "questions": [
    {
      "question_id": "q001",
      "title": "Consumo consciente",
      "prompt": "Você recebeu R$ 50...",
      "difficulty": "facil"
    }
  ]
}
```

### 12.2 Buscar no vector DB

GET:

```powershell
Invoke-RestMethod "http://127.0.0.1:5000/api/vector-search?q=educacao%20financeira%20consumo%20consciente&top_k=3"
```

POST:

```powershell
Invoke-RestMethod `
  -Method POST `
  -Uri "http://127.0.0.1:5000/api/vector-search" `
  -ContentType "application/json" `
  -Body '{"query":"educacao financeira consumo consciente","top_k":3}'
```

Resposta esperada:

```json
{
  "backend": "raw_pdf_tfidf_vector_store",
  "query": "educacao financeira consumo consciente",
  "top_k": 3,
  "results": [
    {
      "rank": 1,
      "similarity": 0.3189,
      "metadata": {
        "source_path": "data/raw/mec_tct/caderno_economia_consolidado_v_final_09_03_2022.pdf",
        "page_number": 47,
        "chunk_id": "chk_..."
      },
      "preview": "PROPOSTA DE MÓDULOS EDUCAÇÃO FINANCEIRA..."
    }
  ]
}
```

### 12.3 Avaliar resposta discursiva

```powershell
Invoke-RestMethod `
  -Method POST `
  -Uri "http://127.0.0.1:5000/api/evaluate" `
  -ContentType "application/json" `
  -Body '{"student_id":"demo","question_id":"q017","student_response":"A dívida cresce porque os juros entram no valor e depois novos juros são calculados sobre esse total."}'
```

Resposta esperada:

```json
{
  "trace_id": "trc_...",
  "response_id": "resp_...",
  "feedback": "...",
  "classification": "...",
  "ambiguity_score": 0.12,
  "human_review_required": false,
  "retrieved_contexts": []
}
```

### 12.4 Consultar trace

```powershell
Invoke-RestMethod http://127.0.0.1:5000/api/traces/trc_EXEMPLO
```

Ou via navegador:

```text
http://127.0.0.1:5000/observability/traces/trc_EXEMPLO
```

---

## 13. Verificação do MVP técnico

O script abaixo valida automaticamente os principais critérios do MVP técnico:

```text
scripts/check_mvp_technical.py
```

### 13.1 Como rodar

Terminal 1:

```powershell
$env:FLASK_DEBUG="0"
python -m flask --app app run --host 127.0.0.1 --port 5000 --no-reload
```

Terminal 2:

```powershell
python .\scripts\check_mvp_technical.py --base-url http://127.0.0.1:5000
```

### 13.2 Resultado esperado

```text
=== Tangram AI Feedback Lab — Technical MVP Check ===

[PASS] question_bank_file
[PASS] vector_manifest
[PASS] student_page_question_dropdown
[PASS] api_questions
[PASS] api_vector_search
[PASS] api_evaluate_trace_id
[PASS] api_evaluate_retrieved_sources
[PASS] api_evaluate_raw_backend
[PASS] api_trace_detail_content
[PASS] trace_persistence
[PASS] human_review_trigger
[PASS] teacher_review_queue_visibility

RESULT: READY for technical MVP demo.
```

### 13.3 Critérios verificados

| Check                             | O que valida                                                    |
| --------------------------------- | --------------------------------------------------------------- |
| `question_bank_file`              | `question_bank.csv` existe, tem 50 questões e três dificuldades |
| `vector_manifest`                 | vector DB foi criado com manifesto, chunks e fontes             |
| `student_page_question_dropdown`  | `/student` usa o question bank                                  |
| `api_questions`                   | API retorna as questões                                         |
| `api_vector_search`               | RAG consulta documentos originais                               |
| `api_evaluate_trace_id`           | avaliação retorna `trace_id`                                    |
| `api_evaluate_retrieved_sources`  | avaliação inclui fontes recuperadas                             |
| `api_evaluate_raw_backend`        | avaliação usa backend raw/TF-IDF                                |
| `api_trace_detail_content`        | trace contém etapas principais                                  |
| `trace_persistence`               | trace foi persistido localmente                                 |
| `human_review_trigger`            | resposta ambígua é roteada para revisão                         |
| `teacher_review_queue_visibility` | revisão aparece em `/teacher/review`                            |

---

## 14. Tracing e rastreabilidade

Cada avaliação deve registrar um trace com etapas como:

```text
privacy_and_preprocessing
retrieval
classification
ambiguity_scoring
feedback_generation
human_review_routing
persistence
```

O trace deve conter, no mínimo:

| Campo                   | Descrição                                     |
| ----------------------- | --------------------------------------------- |
| `trace_id`              | Identificador único do trace                  |
| `response_id`           | Identificador da resposta                     |
| `pseudo_student_id`     | Identificador pseudonimizado                  |
| `student_id_strategy`   | Estratégia usada, por exemplo `pseudonymized` |
| `question_id`           | ID da questão                                 |
| `question_prompt`       | Enunciado                                     |
| `financial_topic`       | Tópico financeiro                             |
| `difficulty`            | Nível de dificuldade                          |
| `bloom_level`           | Nível Bloom                                   |
| `bncc_skill`            | Código demonstrativo ou oficial               |
| `rag_query`             | Query montada para recuperação                |
| `retrieved_contexts`    | Chunks recuperados                            |
| `classification`        | Rótulo pedagógico                             |
| `ambiguity_score`       | Score de ambiguidade                          |
| `feedback`              | Feedback gerado                               |
| `human_review_required` | Indica revisão humana                         |
| `latency_ms`            | Latência por etapa                            |

---

## 15. Human-in-the-loop

O projeto possui fluxo demonstrativo de revisão humana.

### 15.1 Quando uma resposta vai para revisão

Uma resposta pode ser encaminhada para revisão quando:

* possui baixa confiança;
* possui alta ambiguidade;
* é muito curta;
* contém incerteza textual;
* não responde claramente ao enunciado;
* possui potencial PII ou conteúdo sensível;
* o modelo/rubrica não consegue classificar com segurança.

### 15.2 Tela de revisão

Acesse:

```text
http://127.0.0.1:5000/teacher/review
```

A tela deve permitir visualizar respostas pendentes, metadados, feedback gerado e status de revisão.

---

## 16. Active learning

O active learning ainda é demonstrativo.

O fluxo esperado é:

```text
respostas avaliadas
  -> cálculo de ambiguidade/incerteza
  -> seleção de exemplos difíceis
  -> fila de revisão humana
  -> correção por especialista/professor
  -> dataset anotado
  -> futuro re-treinamento/calibração
```

Casos priorizados para anotação:

| Tipo de caso                    | Motivo                        |
| ------------------------------- | ----------------------------- |
| Alta ambiguidade                | Melhora fronteiras de decisão |
| Baixa confiança                 | Ajuda a calibrar modelo       |
| Respostas curtas                | Evita feedback indevido       |
| Discordância rubrica/modelo     | Melhora consistência          |
| Baixa similaridade com exemplos | Captura casos novos           |
| Alto impacto pedagógico         | Reduz risco de feedback ruim  |

---

## 17. MLflow

MLflow é opcional neste mock.

Uso recomendado em versões futuras:

| Recurso MLflow | Uso esperado                                    |
| -------------- | ----------------------------------------------- |
| Experiments    | Comparar modelos e estratégias de feedback      |
| Runs           | Registrar parâmetros, métricas e artifacts      |
| Artifacts      | Salvar datasets, rubricas, relatórios e modelos |
| Model Registry | Promover modelos para staging/produção          |
| Tracing        | Auditar prompts, retrieval, geração e decisão   |

Comando típico para subir a UI:

```bash
mlflow ui
```

Acesse:

```text
http://127.0.0.1:5000
```

Caso a porta conflite com Flask, use outra porta:

```bash
mlflow ui --port 5001
```

---

## 18. Testes

Rodar todos os testes:

```bash
python -m pytest tests -q
```

Rodar testes unitários:

```bash
python -m pytest tests/unit -q
```

Rodar testes de integração:

```bash
python -m pytest tests/integration -q
```

Rodar apenas o checker técnico:

```bash
python scripts/check_mvp_technical.py --base-url http://127.0.0.1:5000
```

---

## 19. Troubleshooting

### 19.1 `WinError 10061`

Erro:

```text
Nenhuma conexão pôde ser feita porque a máquina de destino as recusou ativamente
```

Causa provável: Flask não está rodando ou reiniciou.

Correção:

```powershell
$env:FLASK_DEBUG="0"
python -m flask --app app run --host 127.0.0.1 --port 5000 --no-reload
```

Deixe esse terminal aberto e rode o checker em outro terminal.

---

### 19.2 `WinError 10054`

Erro:

```text
Foi forçado o cancelamento de uma conexão existente pelo host remoto
```

Causa provável: Flask caiu, reiniciou ou fechou a conexão durante uma rota.

Correções:

1. Rodar sem reloader:

```powershell
python -m flask --app app run --host 127.0.0.1 --port 5000 --no-reload
```

2. Verificar o traceback no terminal do Flask.
3. Testar rota por rota.

---

### 19.3 Watchdog reiniciando no Windows

Sintoma:

```text
Detected change in ... sklearn ..., reloading
```

Causa: Flask debug mode com watchdog detectando arquivos alterados em dependências.

Correção:

```powershell
$env:FLASK_DEBUG="0"
python -m flask --app app run --host 127.0.0.1 --port 5000 --no-reload
```

---

### 19.4 `/api/vector-search` retorna 404

Verifique rotas:

```powershell
python -m flask --app app routes
```

A rota esperada é:

```text
/api/vector-search
```

Se não existir, registre a rota no blueprint de API.

---

### 19.5 Backend aparece como fallback

Se a UI ou API mostrar:

```text
seed_tfidf_vector_store
```

em vez de:

```text
raw_pdf_tfidf_vector_store
```

rode novamente:

```powershell
python .\scripts\build_raw_pdf_vector_db.py --raw-dir .\data\raw --processed-dir .\data\processed --vector-dir .\data\vector_store --chunk-size 900 --chunk-overlap 150 --pipeline-version raw_pdf_tfidf_v1.0
```

Depois reinicie o Flask.

---

### 19.6 Warnings `empty_pdf_page_text`

Exemplo:

```text
WARNING empty_pdf_page_text
```

Isso pode acontecer em:

* capa;
* página em branco;
* imagem sem texto extraível;
* tabela escaneada;
* página com conteúdo visual.

Não é necessariamente erro. O pipeline está OK se gerar chunks e manifesto.

---

## 20. Boas práticas já demonstradas

| Prática               | Onde aparece                                                        |
| --------------------- | ------------------------------------------------------------------- |
| Separação por camadas | `app/application`, `app/domain`, `app/infrastructure`, `app/routes` |
| Reprodutibilidade     | scripts e manifestos                                                |
| Auditoria de fontes   | SHA256 dos PDFs e chunks                                            |
| RAG auditável         | source path, page number, chunk ID e preview                        |
| Pseudonimização       | `pseudo_student_id`                                                 |
| Privacy preprocessing | mascaramento de PII                                                 |
| Human-in-the-loop     | fila de revisão                                                     |
| Active learning       | priorização de casos ambíguos                                       |
| Testabilidade         | pytest e checker                                                    |
| Observabilidade       | traces estruturados                                                 |
| Evolução futura       | MLflow, vector DB produtivo, modelos reais                          |

---

## 21. Limitações atuais

| Limitação                             | Impacto                                      |
| ------------------------------------- | -------------------------------------------- |
| Questões ainda são demonstrativas     | Não devem ser usadas como conteúdo oficial   |
| BNCC usa códigos `DEMO`               | Precisa validação pedagógica                 |
| Rubricas são simplificadas            | Não substituem rubrica oficial               |
| TF-IDF não é embedding semântico real | Retrieval inicial, mas limitado              |
| Classificador é baseline/mock         | Não representa desempenho real               |
| Feedback é controlado/template-like   | Ainda não é LLM robusto                      |
| DuckDB/JSONL são locais               | Não servem para produção multiusuário        |
| Não há autenticação                   | Não usar com dados reais                     |
| Não há autorização por perfil         | Aluno/professor/admin ainda não têm ACL real |
| LGPD não está completa                | Apenas demonstra princípios                  |
| Não há deploy produtivo               | Execução local apenas                        |
| Não há avaliação pedagógica formal    | Necessária antes de piloto real              |

---

## 22. Caminho para produção

### 22.1 MVP técnico

* question bank funcional;
* vector DB com fontes originais;
* RAG via API/UI;
* feedback controlado;
* trace auditável;
* human review;
* checker passando.

### 22.2 MVP pedagógico

* questões reais da Tangram;
* rubricas oficiais;
* validação BNCC;
* validação Bloom;
* corpus real anonimizável;
* interface de anotação;
* concordância interanotador;
* revisão humana obrigatória.

### 22.3 Piloto escolar

* professores reais;
* estudantes reais com consentimento;
* coleta controlada;
* avaliação de clareza do feedback;
* análise de erros;
* melhoria de rubricas;
* medição de engajamento.

### 22.4 Produção assistida

* automação apenas para alta confiança;
* revisão humana para casos ambíguos;
* logs e auditoria;
* autenticação;
* autorização;
* LGPD;
* monitoramento de latência, custo e qualidade.

### 22.5 Produção escalável

* Postgres;
* object storage;
* vector DB produtivo;
* filas assíncronas;
* CI/CD;
* Docker;
* observabilidade;
* rollback de modelos;
* versionamento de datasets;
* Model Registry;
* governança de IA.

---

## 23. Possíveis evoluções técnicas

| Área            | Evolução recomendada                                                     |
| --------------- | ------------------------------------------------------------------------ |
| Vector DB       | Chroma, FAISS, Qdrant, pgvector, OpenSearch                              |
| Embeddings      | sentence-transformers, BERTimbau, multilingual-e5, embeddings comerciais |
| Classificação   | Logistic Regression, LightGBM, BERTimbau, DeBERTa, LLM fine-tuning       |
| Feedback        | RAG + template controlado, LLM com guardrails, LLM-as-judge              |
| Persistência    | Postgres + Alembic                                                       |
| Filas           | Celery, RQ, Kafka, Pub/Sub                                               |
| Observabilidade | MLflow, Prometheus, Grafana, OpenTelemetry                               |
| Segurança       | OAuth/OIDC, RBAC, secrets manager                                        |
| Deploy          | Docker, Kubernetes, cloud/on-prem                                        |

---

## 24. Governança e LGPD

Antes de qualquer uso real, implementar:

* consentimento e base legal;
* minimização de dados;
* pseudonimização;
* anonimização para treino;
* detecção e mascaramento de PII;
* controle de acesso por perfil;
* auditoria de acesso;
* retenção e descarte;
* política de exclusão;
* revisão humana;
* documentação de modelo;
* documentação de dados;
* avaliação de viés;
* canal de contestação de feedback.

Dados de menores exigem cuidado adicional e validação jurídica específica.

---

## 25. Comandos úteis

### Listar rotas Flask

```powershell
python -m flask --app app routes
```

### Rodar Flask

```powershell
$env:FLASK_DEBUG="0"
python -m flask --app app run --host 127.0.0.1 --port 5000 --no-reload
```

### Gerar vector DB

```powershell
python .\scripts\build_raw_pdf_vector_db.py --raw-dir .\data\raw --processed-dir .\data\processed --vector-dir .\data\vector_store --chunk-size 900 --chunk-overlap 150 --pipeline-version raw_pdf_tfidf_v1.0
```

### Consultar vector DB via CLI

```powershell
python .\scripts\query_raw_vector_db.py "educação financeira consumo consciente" --top-k 5
```

### Consultar vector DB via API

```powershell
Invoke-RestMethod "http://127.0.0.1:5000/api/vector-search?q=educacao%20financeira%20consumo%20consciente&top_k=3"
```

### Avaliar resposta

```powershell
Invoke-RestMethod `
  -Method POST `
  -Uri "http://127.0.0.1:5000/api/evaluate" `
  -ContentType "application/json" `
  -Body '{"student_id":"demo","question_id":"q017","student_response":"A dívida cresce porque os juros entram no valor e depois novos juros são calculados sobre esse total."}'
```

### Rodar checker técnico

```powershell
python .\scripts\check_mvp_technical.py --base-url http://127.0.0.1:5000
```

### Rodar testes

```powershell
python -m pytest tests -q
```

---

## 26. Interpretação executiva

Este laboratório demonstra uma arquitetura plausível para a Tangram evoluir de correção objetiva para feedback discursivo com IA.

A proposta técnica não depende de automação cega. Ela combina:

```text
IA + RAG + rubricas + rastreabilidade + revisão humana + active learning
```

O valor do MVP técnico é provar que a solução pode ser:

* auditável;
* reproduzível;
* extensível;
* pedagogicamente controlável;
* preparada para governança;
* compatível com evolução para modelos mais robustos.

O principal diferencial arquitetural é não tratar o LLM como uma “caixa mágica”, mas como parte de um sistema controlado por dados, rubricas, fontes, traces, revisão humana e métricas.

---

## 27. Licença e uso

Este projeto é um mock/laboratório técnico para demonstração.

Antes de redistribuir documentos, modelos, datasets ou textos extraídos, verificar:

* licença dos documentos;
* direitos autorais;
* termos de uso;
* LGPD;
* autorização institucional;
* políticas da plataforma Tangram;
* restrições de uso educacional com menores.

---

## 28. Status atual resumido

```text
Question bank demo                  OK
Dropdown de questões                OK
PDFs originais                      OK
Vector DB local                     OK
Busca RAG CLI                       OK
Busca RAG API                       OK
Avaliação via API                   OK
Trace estruturado                   OK
Human review demonstrativo          OK
Checker técnico                     OK, quando todas as rotas estão registradas
Pronto para produção                NÃO
Pronto para demo técnica local       SIM, RESULT: READY for technical MVP demo.
```
