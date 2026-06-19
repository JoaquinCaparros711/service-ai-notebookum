"""Consul service registration — runs once on startup in a background thread."""

import logging
import os
import socket
import threading
import time

import requests

logger = logging.getLogger(__name__)

_CONSUL_URL = os.environ.get("CONSUL_URL", "http://consul:8500")

_AI_DEFAULT_TAGS = [
    "traefik.enable=true",
    "traefik.http.routers.ai.rule=Host(`ai.universidad.localhost`)",
    "traefik.http.routers.ai.entryPoints=https",
    "traefik.http.routers.ai.tls=true",
    "traefik.http.routers.ai.middlewares=cors-ai",
    "traefik.http.middlewares.cors-ai.headers.accesscontrolalloworiginlist=*",
    "traefik.http.middlewares.cors-ai.headers.accesscontrolallowmethods=GET,POST,OPTIONS",
    "traefik.http.middlewares.cors-ai.headers.accesscontrolallowheaders=Content-Type,Authorization",
    "traefik.http.middlewares.cors-ai.headers.addvaryheader=true",
    "traefik.http.services.ai.loadbalancer.server.port=5000",
]


def register_ai(port: int = 5000) -> None:
    """Register the AI service with Consul on startup."""
    threading.Thread(
        target=_register_with_retry,
        args=("ai", port),
        daemon=True,
    ).start()


def _register_with_retry(service_name: str, port: int) -> None:
    from app.utils.consul_kv import get_list
    hostname = socket.gethostname()
    service_id = f"{service_name}-{hostname}"

    for attempt in range(10):
        try:
            tags = get_list("traefik_tags", _AI_DEFAULT_TAGS)
            payload = {
                "ID": service_id,
                "Name": service_name,
                "Address": hostname,
                "Port": port,
                "Tags": tags,
                "Check": {
                    "HTTP": f"http://{hostname}:{port}/health",
                    "Interval": "15s",
                    "Timeout": "5s",
                    "DeregisterCriticalServiceAfter": "30s",
                },
            }
            resp = requests.put(
                f"{_CONSUL_URL}/v1/agent/service/register",
                json=payload,
                timeout=5,
            )
            if resp.status_code == 200:
                logger.info("Registered with Consul as %s", service_id)
                return
            logger.warning("Consul registration HTTP %s", resp.status_code)
        except Exception as exc:
            logger.warning("Consul registration attempt %d failed: %s", attempt + 1, exc)
        time.sleep(5)

    logger.error("Failed to register with Consul after %d attempts", 10)
