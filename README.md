# Service AI NotebookUm

Este microservicio concentra la capa de IA que antes vivía dentro de NotebookUm.

## Endpoints
- `GET /` devuelve un mensaje de disponibilidad.
- `GET /api/v1` devuelve el mismo mensaje bajo el prefijo versionado.
- `GET /health` devuelve el estado del servicio.
- `GET /api/v1/health` devuelve el estado del servicio bajo el prefijo versionado.
- `POST /api/chat` recibe `{ "message": "..." }` y devuelve `{ "response": "..." }`.
- `POST /api/summarize` recibe `{ "text": "...", "language": "es|en" }` y devuelve `{ "summary": "..." }`.
- `POST /api/v1/summaries` recibe `{ "text": "...", "language": "es|en", "document_id": "..." }` y devuelve `{ "summary": "...", "document_id": "..." }`.
- `POST /api/upload` o `POST /api/v1/documento/upload` recibe un PDF en `multipart/form-data` con el campo `file`, extrae su texto y devuelve `{ "document_id": "...", "file_name": "...", "summary": "...", "extracted_text": "..." }`.

## Ejecución con Docker
```bash
docker-compose up -d --build
```

El servicio escucha en el puerto `5002`.
Configura `.env` con `OPENAI_API_KEY` para ChatGPT/OpenAI, o `GEMMA_API_KEY` y `GEMMA_API_URL` para un endpoint compatible con Gemma. Opcionalmente define `GEMMA_MODEL` y `SUMMARY_MODEL`.
El tamaño máximo de subida es de `25 MB`.
