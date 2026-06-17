# Tangram AI Feedback Lab

Este mock demonstra uma suíte completa, porém não produtiva, para avaliação discursiva com IA em educação financeira.

## Tese técnica

A solução não deve ser uma chamada genérica para LLM. Ela deve ser uma esteira rastreável:

![Tese técnica](images/technical_thesis_pipeline.png)

```mermaid
flowchart LR
    A[Dado bem curado] --> B[Rubrica pedagógica]
    B --> C[Modelo leve rastreável]
    C --> D[Ambiguidade e human-in-the-loop]
    D --> E[Feedback controlado]
    E --> F[Tracing, MLflow e melhoria contínua]
```

## Paleta

- Anotação/revisão: roxo suave, cinza e branco.
- Gamificação: roxo + verde com baixa saturação.
- Alertas: amarelo queimado e vermelho suave.
