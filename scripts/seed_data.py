from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import csv

from app.bootstrap import build_seed_rubrics

SEED_DIR = Path("data/seed")

BNCC_ROWS = [
    {
        "document_id": "bncc_demo_consumo_ef",
        "code": "BNCC-DEMO-MAT-FIN-001",
        "title": "BNCC demo: consumo consciente",
        "stage": "Ensino Fundamental",
        "grade_range": "6º ao 9º ano",
        "area": "Matemática / Educação Financeira",
        "topic": "consumo_consciente",
        "skill_text": "Analisar escolhas de consumo, diferenciar necessidade e desejo, justificar decisões financeiras em situações cotidianas e considerar consequências futuras.",
        "keywords": "consumo consciente necessidade desejo planejamento decisão financeira poupança prioridade",
        "notes": "Recorte demonstrativo para mock. Validar contra a BNCC oficial antes de uso real.",
        "version": "v0.1",
    },
    {
        "document_id": "bncc_demo_orcamento_ef",
        "code": "BNCC-DEMO-MAT-FIN-002",
        "title": "BNCC demo: orçamento pessoal",
        "stage": "Ensino Fundamental",
        "grade_range": "7º ao 9º ano",
        "area": "Matemática / Educação Financeira",
        "topic": "orcamento_pessoal",
        "skill_text": "Aplicar noções de renda, despesa, reserva e prioridade para organizar um orçamento simples e interpretar escolhas financeiras.",
        "keywords": "orçamento renda despesa reserva prioridade planejamento gastos",
        "notes": "Recorte demonstrativo para mock. Validar contra a BNCC oficial antes de uso real.",
        "version": "v0.1",
    },
    {
        "document_id": "bncc_demo_juros_em",
        "code": "BNCC-DEMO-MAT-FIN-003",
        "title": "BNCC demo: juros compostos",
        "stage": "Ensino Médio",
        "grade_range": "1ª à 3ª série",
        "area": "Matemática / Educação Financeira",
        "topic": "juros_compostos",
        "skill_text": "Avaliar situações que envolvem juros, crescimento acumulado, tempo, montante e tomada de decisão financeira de médio e longo prazo.",
        "keywords": "juros compostos montante tempo investimento dívida crescimento acumulado",
        "notes": "Recorte demonstrativo para mock. Validar contra a BNCC oficial antes de uso real.",
        "version": "v0.1",
    },
    {
        "document_id": "bncc_demo_argumentacao",
        "code": "BNCC-DEMO-MAT-ARG-001",
        "title": "BNCC demo: argumentação matemática",
        "stage": "Ensino Fundamental e Médio",
        "grade_range": "6º ano à 3ª série",
        "area": "Matemática",
        "topic": "argumentacao",
        "skill_text": "Construir justificativas, explicar procedimentos, comparar alternativas e comunicar raciocínios usando linguagem adequada ao contexto.",
        "keywords": "argumentação justificar explicar comparar alternativas raciocínio clareza coerência",
        "notes": "Recorte demonstrativo para avaliar respostas discursivas.",
        "version": "v0.1",
    },
]

BLOOM_ROWS = [
    {"document_id": "bloom_lembrar", "order": "1", "level": "lembrar", "description": "Reconhecer ou recuperar informação previamente apresentada.", "student_action_examples": "definir listar identificar nomear", "feedback_implication": "Peça ao estudante para retomar o conceito central antes de justificar.", "keywords": "lembrar reconhecer identificar definir listar", "version": "v0.1"},
    {"document_id": "bloom_compreender", "order": "2", "level": "compreender", "description": "Explicar uma ideia com as próprias palavras e interpretar seu significado.", "student_action_examples": "explicar resumir interpretar exemplificar", "feedback_implication": "Valorize a explicação e peça um exemplo cotidiano.", "keywords": "compreender explicar interpretar exemplo significado", "version": "v0.1"},
    {"document_id": "bloom_aplicar", "order": "3", "level": "aplicar", "description": "Usar um conceito ou procedimento em uma situação concreta.", "student_action_examples": "calcular aplicar escolher organizar resolver", "feedback_implication": "Peça que conecte a escolha financeira ao procedimento ou critério usado.", "keywords": "aplicar usar resolver calcular organizar", "version": "v0.1"},
    {"document_id": "bloom_analisar", "order": "4", "level": "analisar", "description": "Separar partes, comparar alternativas e explicar relações de causa e consequência.", "student_action_examples": "comparar diferenciar justificar priorizar relacionar", "feedback_implication": "Peça que explicite critérios de comparação e consequências da decisão.", "keywords": "analisar comparar diferenciar justificar consequência prioridade", "version": "v0.1"},
    {"document_id": "bloom_avaliar", "order": "5", "level": "avaliar", "description": "Julgar uma opção com base em critérios e defender uma decisão.", "student_action_examples": "avaliar decidir argumentar defender criticar", "feedback_implication": "Peça justificativa baseada em critérios, riscos e benefícios.", "keywords": "avaliar decidir argumentar critério risco benefício", "version": "v0.1"},
    {"document_id": "bloom_criar", "order": "6", "level": "criar", "description": "Produzir uma solução, plano ou estratégia original combinando conhecimentos.", "student_action_examples": "planejar propor criar desenhar estratégia", "feedback_implication": "Incentive o estudante a propor um plano financeiro completo e realista.", "keywords": "criar propor planejar estratégia solução", "version": "v0.1"},
]

FINANCIAL_CONCEPT_ROWS = [
    {"document_id": "concept_consumo_consciente", "concept": "consumo_consciente", "definition": "Escolha de consumo feita com base em necessidades, prioridades, orçamento e consequências futuras.", "common_misconceptions": "Achar que todo dinheiro disponível deve ser gasto imediatamente. Confundir desejo com necessidade.", "feedback_hint": "Peça ao estudante para explicar critério de escolha e consequência futura.", "keywords": "consumo consciente necessidade desejo prioridade orçamento guardar", "version": "v0.1"},
    {"document_id": "concept_orcamento_pessoal", "concept": "orcamento_pessoal", "definition": "Organização de renda, despesas, reserva e objetivos para orientar decisões financeiras.", "common_misconceptions": "Listar gastos sem priorização. Ignorar reserva e despesas fixas.", "feedback_hint": "Peça separação entre despesas essenciais, variáveis e reserva.", "keywords": "orçamento renda despesa reserva planejamento mensal", "version": "v0.1"},
    {"document_id": "concept_juros_compostos", "concept": "juros_compostos", "definition": "Juros calculados sobre o montante acumulado, fazendo o valor crescer de forma acelerada com o tempo.", "common_misconceptions": "Tratar juros compostos como acréscimos fixos e lineares.", "feedback_hint": "Peça menção explícita ao tempo e ao crescimento sobre o montante acumulado.", "keywords": "juros compostos montante tempo crescimento acumulado investimento dívida", "version": "v0.1"},
    {"document_id": "concept_dividendos", "concept": "dividendos", "definition": "Parcela do lucro distribuída por uma empresa aos acionistas, relevante para renda passiva e educação financeira de longo prazo.", "common_misconceptions": "Confundir dividendo com rendimento garantido ou com valorização imediata da ação.", "feedback_hint": "Peça diferença entre renda, patrimônio, risco e horizonte de investimento.", "keywords": "dividendos ações renda passiva lucro acionista longo prazo", "version": "v0.1"},
]


def main() -> None:
    """Write synthetic seed rubrics, BNCC/Bloom snippets and responses."""
    SEED_DIR.mkdir(parents=True, exist_ok=True)
    _write_csv(SEED_DIR / "bncc_financial_education_demo.csv", BNCC_ROWS)
    _write_csv(SEED_DIR / "bloom_taxonomy.csv", BLOOM_ROWS)
    _write_csv(SEED_DIR / "financial_concepts.csv", FINANCIAL_CONCEPT_ROWS)

    rubrics = build_seed_rubrics()
    with (SEED_DIR / "rubrics_bncc_bloom.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rubrics[0].__dict__.keys()))
        writer.writeheader()
        for rubric in rubrics:
            writer.writerow(rubric.__dict__)

    responses = [
        {
            "question_id": "q_consumo_001",
            "student_response": "Eu guardaria uma parte para usar no futuro e gastaria só com o necessário.",
            "label": "correct",
        },
        {
            "question_id": "q_consumo_001",
            "student_response": "Eu compraria tudo porque dinheiro é para gastar.",
            "label": "incorrect",
        },
        {
            "question_id": "q_consumo_001",
            "student_response": "Não sei.",
            "label": "vague",
        },
    ]
    _write_csv(SEED_DIR / "synthetic_student_answers.csv", responses)
    print(f"Seed files written to {SEED_DIR}")


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
