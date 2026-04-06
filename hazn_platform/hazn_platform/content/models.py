"""Content domain models: BrandVoice, ApprovedCopy.

These store brand voice definitions and approved copy with
pgvector embeddings for semantic search.
"""

import uuid

from django.db import models
from pgvector.django import VectorField

from hazn_platform.core.models import EndClient


class BrandVoice(models.Model):
    """A brand voice definition for an end-client.

    Uses append-only versioning: new versions are created as new rows.
    Only one BrandVoice per end_client can be active (is_active=True)
    at any given time, enforced by a conditional unique constraint.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    end_client = models.ForeignKey(
        EndClient,
        on_delete=models.CASCADE,
        related_name="brand_voices",
    )
    content = models.TextField()
    embedding = VectorField(dimensions=1536, null=True, blank=True)
    version = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["end_client", "is_active"],
                condition=models.Q(is_active=True),
                name="unique_active_brand_voice_per_client",
            ),
        ]

    def __str__(self):
        return f"BrandVoice v{self.version} ({'active' if self.is_active else 'inactive'})"


class ApprovedCopy(models.Model):
    """Approved copy content with embedding for semantic search.

    Can optionally link to a marketing Campaign (SET_NULL on delete).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    end_client = models.ForeignKey(
        EndClient,
        on_delete=models.CASCADE,
        related_name="approved_copies",
    )
    copy_type = models.CharField(max_length=100)
    content = models.TextField()
    embedding = VectorField(dimensions=1536, null=True, blank=True)
    campaign = models.ForeignKey(
        "marketing.Campaign",
        on_delete=models.SET_NULL,
        related_name="approved_copies",
        null=True,
        blank=True,
    )
    version = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "approved copies"

    def __str__(self):
        return f"{self.copy_type} v{self.version}"
