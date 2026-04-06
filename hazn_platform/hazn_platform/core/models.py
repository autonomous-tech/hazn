"""Core domain models: Agency, EndClient, VaultCredential.

These represent the L2 (agency) and L3 (end-client) hierarchy,
plus credential storage references pointing to HashiCorp Vault.
"""

import uuid

from django.db import models


class Agency(models.Model):
    """L2 entity -- a marketing agency using the Hazn platform."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    house_style = models.JSONField(default=dict, blank=True)
    methodology = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "agencies"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.pk and Agency.objects.exists():
            raise ValueError("Only one Agency instance is allowed.")
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        """Load the singleton Agency, creating default if needed."""
        obj, _ = cls.objects.get_or_create(
            defaults={"name": "Hazn", "slug": "hazn"}
        )
        return obj

    def __str__(self):
        return self.name


class EndClient(models.Model):
    """L3 entity -- a client of an agency. Each belongs to exactly one Agency."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agency = models.ForeignKey(
        Agency,
        on_delete=models.CASCADE,
        related_name="end_clients",
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    competitors = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("agency", "slug")]
        ordering = ["name"]

    def __str__(self):
        return f"{self.agency.name} / {self.name}"


class VaultCredential(models.Model):
    """Reference to a secret stored in HashiCorp Vault.

    Stores only the vault_secret_id (a path like 'secret/data/ga4/api-key'),
    NEVER the raw secret itself.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agency = models.ForeignKey(
        Agency,
        on_delete=models.CASCADE,
        related_name="vault_credentials",
        null=True,
        blank=True,
    )
    end_client = models.ForeignKey(
        EndClient,
        on_delete=models.CASCADE,
        related_name="vault_credentials",
        null=True,
        blank=True,
    )
    service_name = models.CharField(max_length=100)
    vault_secret_id = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("end_client", "service_name")]

    def __str__(self):
        return self.service_name


class MemoryCorrection(models.Model):
    """Audit record for memory corrections (soft-delete + replacement).

    Every time a craft learning is corrected via correct_memory(),
    a MemoryCorrection is created capturing who, when, why, and
    the original vs corrected content.  The replacement_passage_id
    is nullable for pure deletion without replacement.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent_id = models.CharField(max_length=255)
    original_passage_id = models.CharField(max_length=255)
    replacement_passage_id = models.CharField(
        max_length=255, null=True, blank=True
    )
    original_content = models.TextField()
    corrected_content = models.TextField()
    reason = models.TextField()
    corrected_by = models.CharField(max_length=255)
    end_client = models.ForeignKey(
        EndClient,
        on_delete=models.CASCADE,
        related_name="memory_corrections",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Correction {self.pk} by {self.corrected_by}"
