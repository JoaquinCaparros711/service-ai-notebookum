# 🤖 Service AI NotebookUm

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0+-darkgreen.svg?style=flat-square&logo=flask&logoColor=white)
![Consul](https://img.shields.io/badge/Consul-1.15+-red.svg?style=flat-square&logo=hashicorp&logoColor=white)
![OpenAI/Nvidia LLM](https://img.shields.io/badge/LLM-NVIDIA_OpenAI-orange.svg?style=flat-square)
![Redis](https://img.shields.io/badge/Redis-7.0+-red.svg?style=flat-square&logo=redis&logoColor=white)

Este microservicio concentra la **inteligencia artificial y el procesamiento del modelo de lenguaje (LLM)** de la plataforma NotebookUm. Ofrece capacidades distribuidas de chat conversacional, generación automatizada de resúmenes y la ingesta rápida de documentos estructurados.

---

## 📋 Responsabilidades

- **Interacción Conversacional (Chat):** Procesar e interactuar con el usuario mediante un flujo conversacional inteligente basado en contexto.
- **Resúmenes Automáticos:** Sintetizar contenidos documentales en múltiples idiomas (español e inglés) con modelos de lenguaje avanzados.
- **Caché de Extracciones:** Acelerar el acceso al texto y a los resúmenes generados apoyándose en una estructura de almacenamiento rápido con Redis.
- **Gestión de Carga (PDF Upload):** Orquestar la subida multipart de archivos PDF, delegar la extracción de texto y consolidar el resumen resultante en una sola operación.

---

## ⚡ Características Clave

- **Integración con Modelos Avanzados:** Integración nativa por defecto con APIs compatibles de OpenAI y NVIDIA (ej. Nemotron-3, GPT).
- **Límite de Ingesta:** Límite máximo de carga robusto configurado a **25 MB** por archivo PDF.
- **Lectura Transparente de Consul:** Las claves de configuración y credenciales del servicio de IA se recuperan de manera centralizada de Consul KV al inicio.
- **Segregación de Entornos:** Configuraciones específicas y limpias para entornos de pruebas unitarias (`TestingConfig`), desarrollo (`DevelopmentConfig`) y producción (`ProductionConfig`).

---

## 🌐 Endpoints de la API

| Método | Ruta | Autenticación | Entrada (JSON / Multipart) | Descripción |
| :--- | :--- | :---: | :--- | :--- |
| **GET** | `/` | Ninguna | - | Retorna mensaje de disponibilidad básica. |
| **GET** | `/api/v1` | Ninguna | - | Retorna mensaje de disponibilidad versionado. |
| **GET** | `/health` | Ninguna | - | Estado de salud del microservicio. |
| **GET** | `/api/v1/health` | Ninguna | - | Estado de salud versionado. |
| **POST** | `/api/chat` | Ninguna / Gateway | `{ "message": "..." }` | Envía un mensaje y recibe respuesta conversacional. |
| **POST** | `/api/summarize` | Ninguna / Gateway | `{ "text": "...", "language": "es/en" }` | Genera un resumen a partir de un texto plano provisto. |
| **POST** | `/api/v1/summaries`| Ninguna / Gateway | `{ "text": "...", "language": "es/en", "document_id": "..." }` | Genera y asocia un resumen a un ID de documento específico. |
| **POST** | `/api/upload`<br>`/api/v1/documento/upload` | **JWT** (vía Gateway) | `multipart/form-data` con campo `file` | Sube un archivo PDF, extrae su contenido textual, genera un resumen y devuelve el objeto consolidado. |

---

## ⚙️ Configuración centralizada (Consul KV)

Las claves de configuración se leen desde el prefijo raíz `notebookum/ai` en Consul. Si la clave no se encuentra o el almacén está inaccesible, se utilizan los siguientes valores de respaldo predeterminados:

| Clave en Consul KV | Variable de Entorno Inyectada | Valor por Defecto | Descripción |
| :--- | :--- | :--- | :--- |
| `nvidia_api_key` | `NVIDIA_API_KEY` | `""` | Clave secreta de autenticación de la API del LLM. |
| `ai_base_url` | `AI_BASE_URL` | `https://integrate.api.nvidia.com/v1` | Endpoint base para llamadas al modelo LLM compatible. |
| `chat_model` | `CHAT_MODEL` | `nvidia/nemotron-3-ultra-550b-a55b` | Nombre del modelo a utilizar para las conversaciones de chat. |
| `summary_model` | `SUMMARY_MODEL` | `nvidia/nemotron-3-ultra-550b-a55b` | Nombre del modelo a utilizar para resumir texto. |
| `redis_host` | `REDIS_HOST` | `redis` | Servidor de base de datos Redis. |
| `redis_port` | `REDIS_PORT` | `6379` | Puerto de conexión para Redis. |
| `redis_password` | `REDIS_PASSWORD` | `""` | Contraseña para la instancia de Redis. |

---

## 🚀 Despliegue y Ejecución

### Ejecución Local

1. Instalar las dependencias de Python necesarias:
   ```bash
   pip install -r requirements.txt
   ```

2. Configurar la URL de Consul y arrancar el servidor Flask:
   ```bash
   export FLASK_ENV=development
   export CONSUL_URL=http://localhost:8500
   flask run --port=5002
   ```

### Despliegue en Docker

El microservicio utiliza balanceo de carga detrás de Traefik mediante la configuración del archivo `docker-compose.yml`:

```bash
docker-compose up -d --build
```
Una vez activo, cargará automáticamente sus claves de Consul y se registrará en la red para procesar solicitudes de IA de forma segura.
