from app.infrastructure.privacy.pii_redactor import PIIRedactor
from app.infrastructure.privacy.pseudonymizer import Pseudonymizer


def test_pseudonymizer_is_stable_and_hides_original() -> None:
    pseudonymizer = Pseudonymizer("salt")
    first = pseudonymizer.pseudonymize("gabriel@example.com")
    second = pseudonymizer.pseudonymize("gabriel@example.com")
    assert first == second
    assert "gabriel" not in first
    assert first.startswith("stu_")


def test_pii_redactor_masks_email_cpf_and_phone() -> None:
    text = "Meu email é a@b.com, CPF 123.456.789-10 e telefone 1199999-9999."
    redacted = PIIRedactor().redact(text)
    assert "[EMAIL]" in redacted
    assert "[CPF]" in redacted
    assert "[TELEFONE]" in redacted
