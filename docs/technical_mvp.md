# MVP técnico

Esta página resume os dois diagramas adicionais do MVP técnico local.

## Fluxo ponta a ponta

![MVP técnico ponta a ponta](images/technical_mvp_end_to_end.png)

## Mapa de rotas/API

![Mapa de rotas/API](images/api_route_map.png)

## Critério de prontidão

O MVP técnico está pronto para demo local quando o checker retorna `READY for technical MVP demo` e as rotas principais estão registradas:

```bash
python -m flask --app app routes
python scripts/check_mvp_technical.py --base-url http://127.0.0.1:5000
```
