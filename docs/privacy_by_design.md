# Privacidade by design

![Privacidade by design](images/privacy_by_design_flow.png)

```mermaid
flowchart LR
    A[Dado bruto] --> B[Minimização]
    B --> C[Pseudonimização]
    C --> D[Redação de PII]
    D --> E[Dataset pedagógico]
    E --> F[Controle de acesso]
    F --> G[Logs auditáveis]
    G --> H[Retenção definida]
```

Princípios:

- Não enviar nome do estudante ao modelo.
- Separar dado pessoal de dado pedagógico.
- Mascarar PII em texto livre.
- Registrar consentimento e finalidade.
- Versionar dados, rubricas e modelos.
