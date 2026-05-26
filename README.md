# Service AI NotebookUm

Este microservicio concentra la capa de IA que antes vivía dentro de NotebookUm.

## Endpoints
- `GET /` devuelve un mensaje de disponibilidad.
- `GET /health` devuelve el estado del servicio.
- `POST /api/chat` recibe `{ "message": "..." }` y devuelve `{ "response": "..." }`.
- `POST /api/summarize` recibe `{ "text": "...", "language": "es|en" }` y devuelve `{ "summary": "..." }`.

## Ejecución con Docker
```bash
docker-compose up -d --build
```

El servicio escucha en el puerto `5002`.
Configura `.env` con `OPENAI_API_KEY` o `GEMMA_API_KEY`, y opcionalmente `GEMMA_API_URL`.
