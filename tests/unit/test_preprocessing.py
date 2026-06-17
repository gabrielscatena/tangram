from app.infrastructure.preprocessing.text_preprocessor import TextPreprocessor


def test_clean_collapses_whitespace_and_control_chars() -> None:
    cleaned = TextPreprocessor().clean("  Quero\n\tguardar   dinheiro.  ")
    assert cleaned == "Quero guardar dinheiro."


def test_tokenize_for_rules_returns_lowercase_tokens() -> None:
    tokens = TextPreprocessor().tokenize_for_rules("Guardar R$ 50 é necessário!")
    assert "guardar" in tokens
    assert "necessário" in tokens
