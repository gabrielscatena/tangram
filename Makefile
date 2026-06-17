.PHONY: init seed vector train test run docs-serve mlflow-ui clean

init:
	python scripts/init_db.py
	python scripts/seed_data.py
	python scripts/build_vector_store.py

seed:
	python scripts/seed_data.py

vector:
	python scripts/build_vector_store.py

train:
	python scripts/train_baseline_classifier.py

test:
	python -m pytest tests -q

run:
	flask --app app:create_app run --debug

docs-serve:
	mkdocs serve

mlflow-ui:
	mlflow ui --backend-store-uri ./mlruns

clean:
	rm -rf .pytest_cache .ruff_cache htmlcov mlruns data/duckdb/*.duckdb data/vector_store/*

raw-vector-db:
	python scripts/build_raw_pdf_vector_db.py --raw-dir data/raw --processed-dir data/processed --vector-dir data/vector_store

query-vector-db:
	python scripts/query_raw_vector_db.py "educação financeira consumo consciente" --top-k 5
