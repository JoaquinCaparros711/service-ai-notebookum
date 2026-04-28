# Service AI NotebookUm

Este microservicio es responsable de **Generar Resúmenes e interactuar con Modelos de Lenguaje** para el sistema NotebookUm.

## Responsabilidades
- Recibe texto estructurado en JSON.
- Se comunica con las APIs de modelos de lenguaje (OpenAI, Nemotron, Gemma).
- Devuelve el texto procesado (resúmenes o respuestas Q&A) en formato JSON.

## Ejecución con Docker
```bash
docker-compose up -d --build
```
El servicio estará disponible internamente en el puerto `5002`.
Asegúrate de configurar tu `.env` con las variables `OPENAI_API_KEY` o `GEMMA_API_KEY`.
