"""Letta client factory for the self-hosted Letta server.

Returns a configured ``letta_client.Letta`` instance using connection
details from Django settings:

* ``LETTA_BASE_URL`` -- Letta server URL (e.g. ``http://letta:8283``)
* ``LETTA_SERVER_PASSWORD`` -- API key / server password
"""

from letta_client import Letta
from django.conf import settings


def get_letta_client() -> Letta:
    """Return a configured Letta client for the self-hosted server.

    The client points at ``settings.LETTA_BASE_URL`` and authenticates
    with ``settings.LETTA_SERVER_PASSWORD``.
    """
    return Letta(
        base_url=settings.LETTA_BASE_URL,
        api_key=settings.LETTA_SERVER_PASSWORD,
    )
