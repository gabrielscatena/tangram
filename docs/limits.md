# Limites do mock

Este pacote não é produtivo.

## Limitações principais

- Dados sintéticos.
- Classificador baseado em regras.
- Rubricas simplificadas.
- Sem autenticação.
- Sem controle de acesso real.
- Sem avaliação formal de fairness.
- Sem teste de carga.
- Sem consentimento real.

## Próximos passos produtivos

![Roadmap até TRL 4](images/mvp_progression_roadmap.png)

```mermaid
flowchart TD
    A[Mock local] --> B[Corpus real consentido]
    B --> C[Anotação dupla]
    C --> D[Validação interanotador]
    D --> E[Baseline ML]
    E --> F[Human-in-the-loop]
    F --> G[Piloto controlado]
    G --> H[TRL 4]
```
