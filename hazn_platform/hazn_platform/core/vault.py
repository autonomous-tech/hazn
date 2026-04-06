"""Vault client helpers for storing and retrieving secrets.

Uses the ``hvac`` Python client to communicate with HashiCorp Vault's
KV v2 secrets engine.  Connection details come from Django settings:

* ``VAULT_ADDR`` -- Vault server URL (e.g. ``http://vault:8200``)
* ``VAULT_ROLE_ID`` -- AppRole Role ID for authentication
* ``VAULT_SECRET_ID`` -- AppRole Secret ID for authentication

Authentication uses the AppRole method with lazy token caching.
The root token is never used by application code.
"""

from __future__ import annotations

import logging

import hvac
from django.conf import settings

logger = logging.getLogger(__name__)

_cached_client: hvac.Client | None = None


def get_vault_client() -> hvac.Client:
    """Return an authenticated Vault client using AppRole credentials.

    Uses lazy token caching: the first call authenticates via AppRole
    and subsequent calls reuse the client until the token expires.

    Raises
    ------
    RuntimeError
        If the client cannot authenticate with the configured AppRole credentials.
    """
    global _cached_client  # noqa: PLW0603

    if _cached_client is not None and _cached_client.is_authenticated():
        return _cached_client

    client = hvac.Client(url=settings.VAULT_ADDR)
    client.auth.approle.login(
        role_id=settings.VAULT_ROLE_ID,
        secret_id=settings.VAULT_SECRET_ID,
    )

    if not client.is_authenticated():
        msg = (
            "Vault client is not authenticated. "
            "Check VAULT_ADDR, VAULT_ROLE_ID, and VAULT_SECRET_ID in Django settings."
        )
        raise RuntimeError(msg)

    _cached_client = client
    return _cached_client


def invalidate_vault_cache() -> None:
    """Clear the cached Vault client.

    Useful for test isolation and forcing re-authentication.
    """
    global _cached_client  # noqa: PLW0603
    _cached_client = None


def store_secret(path: str, data: dict) -> str:
    """Store a secret in Vault KV v2 and return the path.

    Parameters
    ----------
    path:
        Logical path within the ``secret/`` mount (e.g. ``agencies/acme/ga4``).
    data:
        Dictionary of key-value pairs to store.

    Returns
    -------
    str
        The *path* argument, for convenience when creating ``VaultCredential``
        records.
    """
    client = get_vault_client()
    client.secrets.kv.v2.create_or_update_secret(
        path=path,
        secret=data,
        mount_point="secret",
    )
    return path


def delete_secret(path: str) -> bool:
    """Delete a secret from Vault permanently (all versions).

    Returns True on success, False on error (non-fatal).

    Parameters
    ----------
    path:
        Logical path within the ``secret/`` mount.

    Returns
    -------
    bool
        True if deletion succeeded, False if an error occurred.
    """
    try:
        client = get_vault_client()
        client.secrets.kv.v2.delete_metadata_and_all_versions(
            path=path,
            mount_point="secret",
        )
        return True
    except Exception:
        logger.warning("Failed to delete Vault secret at %s", path, exc_info=True)
        return False


def read_secret(path: str) -> dict:
    """Read a secret from Vault KV v2.

    Parameters
    ----------
    path:
        Logical path within the ``secret/`` mount.

    Returns
    -------
    dict
        The secret's key-value data.
    """
    client = get_vault_client()
    response = client.secrets.kv.v2.read_secret_version(
        path=path,
        mount_point="secret",
        raise_on_deleted_version=True,
    )
    return response["data"]["data"]
