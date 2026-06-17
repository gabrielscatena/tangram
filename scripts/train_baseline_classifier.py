from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from pathlib import Path


def main() -> None:
    """Train a tiny baseline classifier and log with MLflow when available.

    This script is demonstrative. The app itself uses a deterministic rule-based classifier
    so the package remains runnable without model artifacts.
    """
    try:
        import pandas as pd
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import accuracy_score, f1_score
        from sklearn.pipeline import Pipeline
    except ImportError as exc:
        raise SystemExit("pandas and scikit-learn are required for this script.") from exc

    path = Path("data/seed/synthetic_student_answers.csv")
    if not path.exists():
        raise SystemExit("Run scripts/seed_data.py first.")

    df = pd.read_csv(path)
    pipeline = Pipeline(
        [
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2))),
            ("clf", LogisticRegression(max_iter=500)),
        ]
    )
    pipeline.fit(df["student_response"], df["label"])
    preds = pipeline.predict(df["student_response"])
    metrics = {
        "train_accuracy": float(accuracy_score(df["label"], preds)),
        "train_macro_f1": float(f1_score(df["label"], preds, average="macro")),
    }

    try:
        import mlflow

        mlflow.set_tracking_uri("file:./mlruns")
        mlflow.set_experiment("tangram-ai-feedback-lab")
        with mlflow.start_run(run_name="baseline_tfidf_logreg_v0"):
            mlflow.log_params({"model": "tfidf_logreg", "mock": True})
            mlflow.log_metrics(metrics)
    except ImportError:
        pass

    print(metrics)


if __name__ == "__main__":
    main()
