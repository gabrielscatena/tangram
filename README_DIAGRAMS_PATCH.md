# Tangram Docs Diagrams Patch v2

Este pacote atualiza `docs/images/` com todos os diagramas PNG do projeto, incluindo os quatro diagramas Mermaid que estavam faltando no pacote anterior.

Gerado em: `2026-06-17T19:20:20.908793+00:00`

## Novos arquivos adicionados

- `docs/images/mlflow_experiment_trace_overview_mermaid.png`
- `docs/images/student_response_full_sequence_mermaid.png`
- `docs/images/application_ports_interfaces_mermaid.png`
- `docs/images/clean_architecture_layers_mermaid_original.png`

## Arquivos Markdown atualizados

- `docs/diagrams.md`
- `docs/architecture.md`
- `docs/workflows.md`
- `docs/mlflow_tracing.md`

## Como aplicar

Extraia este ZIP na raiz do projeto, preservando a estrutura de pastas:

```powershell
Expand-Archive -Force .\tangram_docs_diagrams_patch_v2_complete.zip -DestinationPath .\
```

Depois, se estiver usando MkDocs:

```powershell
mkdocs serve
```

ou abra diretamente:

```text
docs/diagrams.md
```

## Total de diagramas em `docs/images`

18 PNGs.
