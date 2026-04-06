"""Integration tests for Vault client helpers.

Tests require a running, unsealed Vault instance (via Docker Compose).
The conftest.py fixture auto-patches settings.VAULT_ROLE_ID and
settings.VAULT_SECRET_ID from .vault-approle for AppRole authentication.

Test classes:
- TestVaultClient: Basic client creation and secret roundtrip
- TestVaultCredentialIntegration: VaultCredential model + Vault integration
- TestAppRoleAuth: Verify Django AppRole login and read+write capability
- TestPolicyScoping: Verify orchestrator/MCP are read-only, sys/auth denied
- TestTokenCaching: Verify lazy client caching and cache invalidation
"""

import hvac
import hvac.exceptions
import pytest
from django.conf import settings

from hazn_platform.core.vault import get_vault_client
from hazn_platform.core.vault import invalidate_vault_cache
from hazn_platform.core.vault import read_secret
from hazn_platform.core.vault import store_secret


@pytest.mark.integration
class TestVaultClient:
    """Vault authentication and client creation via AppRole."""

    def test_get_vault_client_returns_authenticated_client(self):
        """get_vault_client() should return an hvac.Client that is authenticated."""
        client = get_vault_client()
        assert client.is_authenticated()

    def test_store_and_read_secret_roundtrip(self):
        """store_secret then read_secret should return the same data."""
        secret_data = {"api_key": "sk-test-123", "extra": "value"}
        path = store_secret("agencies/test-roundtrip/creds", secret_data)
        assert path == "agencies/test-roundtrip/creds"

        retrieved = read_secret("agencies/test-roundtrip/creds")
        assert retrieved == secret_data


@pytest.mark.integration
@pytest.mark.django_db
class TestVaultCredentialIntegration:
    """Vault + VaultCredential model integration."""

    def test_vault_credential_stores_path_and_reads_via_helper(self):
        """Create a VaultCredential, store a secret at its path, read it back."""
        from hazn_platform.core.models import Agency
        from hazn_platform.core.models import EndClient
        from hazn_platform.core.models import VaultCredential

        agency = Agency.objects.create(name="Test Agency", slug="test-vault-agency")
        client = EndClient.objects.create(
            agency=agency, name="Test Client", slug="test-vault-client"
        )

        # Store a secret in Vault (path must be under agencies/* per AppRole policy)
        secret_data = {"ga4_key": "test-ga4-key-abc"}
        vault_path = store_secret("agencies/test-vault-cred-int/ga4", secret_data)

        # Create a VaultCredential record pointing to the path
        cred = VaultCredential.objects.create(
            agency=agency,
            end_client=client,
            service_name="ga4",
            vault_secret_id=vault_path,
        )
        cred.refresh_from_db()

        # Read the secret using the VaultCredential's stored path
        retrieved = read_secret(cred.vault_secret_id)
        assert retrieved == secret_data
        # Confirm the model only stores the path, never the secret
        assert "ga4_key" not in str(cred.vault_secret_id)


@pytest.mark.integration
class TestAppRoleAuth:
    """Verify Django AppRole authentication and read+write capability."""

    def test_django_approle_login(self):
        """get_vault_client() authenticates via AppRole, not root token."""
        client = get_vault_client()
        assert client.is_authenticated()
        # Verify we are using AppRole credentials (non-empty role ID in settings)
        assert settings.VAULT_ROLE_ID
        # Ensure VAULT_TOKEN is not set (clean break from root token)
        vault_token = getattr(settings, "VAULT_TOKEN", "")
        assert not vault_token, "VAULT_TOKEN should not be set; using AppRole instead"

    def test_django_read_write(self):
        """Django AppRole can store and read secrets (CRUD policy)."""
        test_path = "agencies/test-policy/ga4"
        secret_data = {"key": "test-value-123", "service": "ga4"}

        # Store (write)
        path = store_secret(test_path, secret_data)
        assert path == test_path

        # Read back
        retrieved = read_secret(test_path)
        assert retrieved == secret_data

        # Clean up: delete the test secret
        client = get_vault_client()
        client.secrets.kv.v2.delete_metadata_and_all_versions(
            path=test_path, mount_point="secret"
        )


@pytest.mark.integration
class TestPolicyScoping:
    """Verify policy isolation: orchestrator/MCP are read-only, sys/auth denied."""

    def _make_client(self, creds, role_id_key, secret_id_key):
        """Create an hvac client authenticated with the given role credentials."""
        client = hvac.Client(url=settings.VAULT_ADDR)
        client.auth.approle.login(
            role_id=creds[role_id_key],
            secret_id=creds[secret_id_key],
        )
        return client

    def test_orchestrator_readonly(self, vault_approle_credentials):
        """Orchestrator role can read secrets but write raises Forbidden."""
        creds = vault_approle_credentials
        test_path = "agencies/test-scoping/creds"

        # Setup: store a secret with Django role (has write access)
        store_secret(test_path, {"setup": "data"})

        try:
            # Create orchestrator client
            orch_client = self._make_client(
                creds, "ORCHESTRATOR_ROLE_ID", "ORCHESTRATOR_SECRET_ID"
            )

            # Read should succeed
            response = orch_client.secrets.kv.v2.read_secret_version(
                path=test_path, mount_point="secret", raise_on_deleted_version=True
            )
            assert response["data"]["data"]["setup"] == "data"

            # Write should raise Forbidden
            with pytest.raises(hvac.exceptions.Forbidden):
                orch_client.secrets.kv.v2.create_or_update_secret(
                    path=test_path,
                    secret={"attempted": "write"},
                    mount_point="secret",
                )
        finally:
            # Clean up with Django role
            django_client = get_vault_client()
            django_client.secrets.kv.v2.delete_metadata_and_all_versions(
                path=test_path, mount_point="secret"
            )

    def test_mcp_readonly(self, vault_approle_credentials):
        """MCP role can read secrets but write raises Forbidden."""
        creds = vault_approle_credentials
        test_path = "agencies/test-scoping-mcp/creds"

        # Setup: store a secret with Django role
        store_secret(test_path, {"setup": "mcp-data"})

        try:
            # Create MCP client
            mcp_client = self._make_client(creds, "MCP_ROLE_ID", "MCP_SECRET_ID")

            # Read should succeed
            response = mcp_client.secrets.kv.v2.read_secret_version(
                path=test_path, mount_point="secret", raise_on_deleted_version=True
            )
            assert response["data"]["data"]["setup"] == "mcp-data"

            # Write should raise Forbidden
            with pytest.raises(hvac.exceptions.Forbidden):
                mcp_client.secrets.kv.v2.create_or_update_secret(
                    path=test_path,
                    secret={"attempted": "write"},
                    mount_point="secret",
                )
        finally:
            # Clean up with Django role
            django_client = get_vault_client()
            django_client.secrets.kv.v2.delete_metadata_and_all_versions(
                path=test_path, mount_point="secret"
            )

    def test_sys_auth_denied(self, vault_approle_credentials):
        """All 3 roles are denied access to sys/* and auth/* paths."""
        creds = vault_approle_credentials
        roles = [
            ("DJANGO_ROLE_ID", "DJANGO_SECRET_ID"),
            ("ORCHESTRATOR_ROLE_ID", "ORCHESTRATOR_SECRET_ID"),
            ("MCP_ROLE_ID", "MCP_SECRET_ID"),
        ]

        for role_id_key, secret_id_key in roles:
            client = self._make_client(creds, role_id_key, secret_id_key)
            with pytest.raises(hvac.exceptions.Forbidden):
                client.sys.list_auth_methods()


@pytest.mark.integration
class TestTokenCaching:
    """Verify lazy client caching and cache invalidation."""

    def test_consecutive_calls_reuse_client(self):
        """Two consecutive get_vault_client() calls return the same cached object."""
        invalidate_vault_cache()
        client1 = get_vault_client()
        client2 = get_vault_client()
        assert client1 is client2

    def test_invalidate_forces_new_client(self):
        """After invalidate_vault_cache(), next call returns a new client."""
        client1 = get_vault_client()
        invalidate_vault_cache()
        client2 = get_vault_client()
        assert client1 is not client2
        assert client2.is_authenticated()
