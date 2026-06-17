# v5 — Question Bank + Raw PDF Vector DB Integration

Esta versão conecta o `Student Playground` ao arquivo `data/seed/question_bank.csv` com 50 questões.

## Fluxo

1. O app carrega `data/seed/question_bank.csv`.
2. A tela `/student` mostra um dropdown com as 50 questões.
3. Ao gerar feedback, o app envia para o use case:
   - pergunta selecionada;
   - resposta do aluno;
   - tópico financeiro;
   - BNCC demo;
   - nível Bloom;
   - resposta esperada.
4. O use case monta uma query RAG com esses campos.
5. Se `data/vector_store/tfidf_vectorizer.joblib`, `tfidf_matrix.npz` e `indexed_chunks.jsonl` existirem, o app usa o vector DB original dos PDFs.
6. Se os artefatos não existirem, o app usa fallback com seeds sintéticos para a UI não quebrar.

## Rodar do zero no PowerShell

```powershell
python .\scripts\build_raw_pdf_vector_db.py --raw-dir .\data\raw --processed-dir .\data\processed --vector-dir .\data\vector_store --chunk-size 900 --chunk-overlap 150 --pipeline-version raw_pdf_tfidf_v1.0
python -m flask --app app run --debug
```

Abra:

```text
http://127.0.0.1:5000/student
```

Na tela, confira o campo `Vector backend`:

- `raw_pdf_tfidf_vector_store`: está usando PDFs originais.
- `seed_tfidf_vector_store`: está usando fallback mock/seeds.

## API

Listar questões:

```powershell
curl http://127.0.0.1:5000/api/questions
```

Avaliar resposta:

```powershell
curl -X POST http://127.0.0.1:5000/api/evaluate -H "Content-Type: application/json" -d '{"student_id":"demo","question_id":"q017","student_response":"A dívida cresce porque os juros entram no valor e depois novos juros são calculados sobre esse total."}'
```
