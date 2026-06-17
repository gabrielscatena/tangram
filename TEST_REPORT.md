# Test Report - v4 raw PDF vector DB pipeline

## Automated tests

```text
python -m pytest tests -q
..................                                                       [100%]
18 passed
```

## Raw PDF pipeline smoke test

```text
python scripts/build_raw_pdf_vector_db.py --raw-dir data/raw --processed-dir data/processed --vector-dir data/vector_store --chunk-size 900 --chunk-overlap 150 --pipeline-version raw_pdf_tfidf_v1.0
{
  "status": "ok",
  "chunks": 1677,
  "manifest": "data/vector_store/vector_index_manifest.json"
}
```

## Vector query smoke test

```text
python scripts/query_raw_vector_db.py "educação financeira consumo consciente" --top-k 3
```

The top results point to the MEC Caderno Economia sections on Educação Financeira.
