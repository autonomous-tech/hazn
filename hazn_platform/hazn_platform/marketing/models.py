"""Marketing domain models: Keyword, Audit, Campaign, Decision.

These track SEO/content marketing data for end-clients:
keyword research, site audits, campaigns, and AI-generated decisions.
"""

import uuid

from django.db import models

from hazn_platform.core.models import EndClient


class Keyword(models.Model):
    """A keyword tracked for an end-client's SEO strategy."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    end_client = models.ForeignKey(
        EndClient,
        on_delete=models.CASCADE,
        related_name="keywords",
    )
    term = models.CharField(max_length=500)
    search_volume = models.IntegerField(null=True, blank=True)
    difficulty = models.FloatField(null=True, blank=True)
    intent = models.CharField(max_length=50)
    status = models.CharField(max_length=50, default="discovered")
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.term} ({self.status})"


class Audit(models.Model):
    """A site or content audit performed for an end-client."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    end_client = models.ForeignKey(
        EndClient,
        on_delete=models.CASCADE,
        related_name="audits",
    )
    audit_type = models.CharField(max_length=100)
    findings = models.JSONField(default=dict, blank=True)
    score = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.audit_type} ({self.score})"


class Campaign(models.Model):
    """A marketing campaign for an end-client."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    end_client = models.ForeignKey(
        EndClient,
        on_delete=models.CASCADE,
        related_name="campaigns",
    )
    name = models.CharField(max_length=255)
    campaign_type = models.CharField(max_length=100)
    status = models.CharField(max_length=50, default="draft")
    config = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.status})"


class Decision(models.Model):
    """An AI-generated or human decision related to an end-client's strategy."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    end_client = models.ForeignKey(
        EndClient,
        on_delete=models.CASCADE,
        related_name="decisions",
    )
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.SET_NULL,
        related_name="decisions",
        null=True,
        blank=True,
    )
    decision_type = models.CharField(max_length=100)
    rationale = models.TextField()
    outcome = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.decision_type}: {self.rationale[:50]}"
