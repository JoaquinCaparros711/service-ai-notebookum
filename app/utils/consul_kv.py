"""Consul KV reader — loads AI service configuration from Consul Key-Value store.

Keys live under the prefix ``notebookum/ai/``.  Every call is synchronous
and blocking: it is meant to be called once at startup (inside Config),
not on every request.

Fall-back chain for each key:
  1. Consul KV  →  ``GET /v1/kv/notebookum/ai/{key}?raw``
  2. Caller-supplied default (usually a hard-coded safe value)

Additionally, this module injects the retrieved values into ``os.environ``
so that legacy code using ``os.environ.get()`` directly still works without
requiring changes throughout the codebase.
"""

import json
import logging
import os

import requests

logger = logging.getLogger(__name__)

_CONSUL_URL = os.environ.get("CONSUL_URL", "http://consul:8500")
_PREFIX = "notebookum/ai"
_TIMEOUT = 3  # seconds — short so startup is not blocked on a missing Consul


def get(key: str, default: str = "") -> str:
    """Return the raw string value for *key* from Consul KV."""
    url = f"{_CONSUL_URL}/v1/kv/{_PREFIX}/{key}?raw"
    try:
        resp = requests.get(url, timeout=_TIMEOUT)
        if resp.status_code == 200:
            value = resp.text.strip()
            logger.debug("consul_kv[ai]: loaded %s/%s", _PREFIX, key)
            return value
        if resp.status_code == 404:
            logger.warning("consul_kv[ai]: key not found — %s/%s (using default)", _PREFIX, key)
        else:
            logger.warning("consul_kv[ai]: GET %s returned HTTP %s (using default)", key, resp.status_code)
    except requests.exceptions.ConnectionError:
        logger.warning("consul_kv[ai]: Consul unreachable at %s (using default for %s)", _CONSUL_URL, key)
    except Exception as exc:
        logger.warning("consul_kv[ai]: unexpected error reading %s: %s (using default)", key, exc)
    return default


def get_int(key: str, default: int) -> int:
    """Convenience wrapper — converts the KV value to int."""
    raw = get(key, str(default))
    try:
        return int(raw)
    except ValueError:
        logger.warning("consul_kv[ai]: key %s value %r is not an integer, using default %d", key, raw, default)
        return default


def get_list(key: str, default: list) -> list:
    """Convenience wrapper — parses a JSON array stored in Consul KV."""
    raw = get(key, "")
    if not raw:
        return default
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("consul_kv[ai]: key %s is not valid JSON (using default)", key)
        return default


# ── Inject all KV-sourced config into os.environ ─────────────────────────────
# This allows existing code that calls os.environ.get("REDIS_HOST") etc.
# to transparently receive values from Consul without requiring refactoring.
_INJECT: dict[str, str] = {
    "NVIDIA_API_KEY": get("nvidia_api_key", os.environ.get("NVIDIA_API_KEY", "")),
    "AI_BASE_URL":    get("ai_base_url",    "https://integrate.api.nvidia.com/v1"),
    "SUMMARY_MODEL":  get("summary_model",  "nvidia/nemotron-3-ultra-550b-a55b"),
    "CHAT_MODEL":     get("chat_model",     "nvidia/nemotron-3-ultra-550b-a55b"),
    "REDIS_HOST":     get("redis_host",     "redis"),
    "REDIS_PORT":     get("redis_port",     "6379"),
    "REDIS_PASSWORD": get("redis_password", ""),
}

for _k, _v in _INJECT.items():
    os.environ[_k] = _v
