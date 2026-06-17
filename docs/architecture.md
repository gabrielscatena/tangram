# Arquitetura

## Arquitetura em camadas

![Arquitetura em camadas](images/clean_architecture_layers.png)

## Arquitetura em camadas — versão Mermaid original

![Arquitetura em camadas — versão Mermaid original](images/clean_architecture_layers_mermaid_original.png)

```mermaid
flowchart TB
    UI[Flask Views / Templates] --> API[Routes / Controllers]
    API --> APP[Application Services]
    APP --> DOMAIN[Domain Models / Use Cases]
    APP --> INFRA[Infrastructure Adapters]
    INFRA --> DB[(DuckDB)]
    INFRA --> VDB[(Vector Store)]
    INFRA --> MLFLOW[MLflow Tracking / Tracing]
    INFRA --> MODELS[Local Models]
```

## Decisão arquitetural

O mock usa uma Clean Architecture leve:

- `domain`: regras, entidades e contratos.
- `application`: casos de uso.
- `infrastructure`: DuckDB, vector retrieval, modelos e tracing.
- `routes/templates`: UI e API.

## Dependências do caso de uso

![Dependências do caso de uso](images/application_use_case_dependencies.png)

## Portas/interfaces da aplicação — versão Mermaid original

![Portas/interfaces da aplicação](images/application_ports_interfaces_mermaid.png)

```mermaid
classDiagram
    class EvaluateResponseUseCase
    class ResponseRepository
    class VectorRetriever
    class ResponseClassifier
    class AmbiguityScorer
    class FeedbackGenerator
    class TraceService

    EvaluateResponseUseCase --> ResponseRepository
    EvaluateResponseUseCase --> VectorRetriever
    EvaluateResponseUseCase --> ResponseClassifier
    EvaluateResponseUseCase --> AmbiguityScorer
    EvaluateResponseUseCase --> FeedbackGenerator
    EvaluateResponseUseCase --> TraceService
```
