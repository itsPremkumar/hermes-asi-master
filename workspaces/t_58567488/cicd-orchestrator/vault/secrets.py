"""Vault-backed secret management for CI/CD pipelines."""

import json
import logging
import os
from typing import Any, Optional

logger = logging.getLogger(__name__)


class SecretManager:
    """Manages secrets with Vault as primary source and env as fallback."""

    def __init__(self, vault_addr: Optional[str] = None, vault_token: Optional[str] = None):
        self.vault_addr = vault_addr or os.environ.get("VAULT_ADDR", "")
        self.vault_token = vault_token or os.environ.get("VAULT_TOKEN", "")
        self._cache: dict[str, dict[str, Any]] = {}

    def get_secret(self, path: str, mount: str = "secret") -> dict[str, Any]:
        """Read a secret from Vault with caching."""
        cache_key = f"{mount}/{path}"
        if cache_key in self._cache:
            logger.debug("Secret cache hit: %s", cache_key)
            return self._cache[cache_key]

        secret = self._read_vault(path, mount)
        if not secret:
            secret = self._env_fallback(path)

        if secret:
            self._cache[cache_key] = secret

        return secret

    def _read_vault(self, path: str, mount: str) -> dict[str, Any]:
        """Read secret from Vault using the hvac client."""
        try:
            import hvac
        except ImportError:
            logger.warning("hvac not installed, using env fallback")
            return {}

        try:
            client = hvac.Client(url=self.vault_addr, token=self.vault_token)
            if not client.is_authenticated():
                logger.warning("Vault not authenticated")
                return {}

            resp = client.secrets.kv.v2.read_secret_version(path=path, mount_point=mount)
            return resp.get("data", {}).get("data", {})
        except Exception as e:
            logger.error("Vault read error for %s: %s", path, e)
            return {}

    def _env_fallback(self, path: str) -> dict[str, Any]:
        """Fall back to environment variables matching the path prefix."""
        prefix = path.replace("/", "_").upper()
        result = {}
        for key, value in os.environ.items():
            if key.startswith(prefix + "_") or key == prefix:
                result[key] = value
        return result

    def rotate_secret(self, path: str, mount: str = "secret") -> bool:
        """Mark a secret for rotation by clearing the cache."""
        cache_key = f"{mount}/{path}"
        if cache_key in self._cache:
            del self._cache[cache_key]
            logger.info("Secret cache cleared for %s", cache_key)
            return True
        return False

    def write_secret(self, path: str, data: dict[str, Any], mount: str = "secret") -> bool:
        """Write a secret to Vault (requires token with write permission)."""
        try:
            import hvac
        except ImportError:
            logger.error("hvac not installed")
            return False

        try:
            client = hvac.Client(url=self.vault_addr, token=self.vault_token)
            if not client.is_authenticated():
                logger.error("Vault not authenticated")
                return False

            client.secrets.kv.v2.create_or_update_secret(
                path=path,
                secret=data,
                mount_point=mount,
            )
            logger.info("Secret written to %s/%s", mount, path)
            return True
        except Exception as e:
            logger.error("Vault write error: %s", e)
            return False