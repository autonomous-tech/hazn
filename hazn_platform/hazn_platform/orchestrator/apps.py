import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)

# Module-level singleton for the ToolRegistry.
# Set by OrchestratorConfig.ready() after build_registry() completes.
_REGISTRY_SINGLETON = None


def _build_registry():
    """Lazy import to avoid circular imports at module level."""
    from hazn_platform.orchestrator.tools import build_registry
    return build_registry()


class OrchestratorConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "hazn_platform.orchestrator"
    verbose_name = "Orchestrator"

    _ready_done = False

    def ready(self):
        """Build ToolRegistry at startup and store as module-level singleton.

        - Creates a fully-populated ToolRegistry via build_registry()
        - All tools are pre-registered by build_registry() (no separate wire step)
        - Stores registry as module-level singleton for runtime use

        Wraps everything in try/except to avoid crashing Django startup.
        Guards against Django's double-ready call with _ready_done flag.
        """
        global _REGISTRY_SINGLETON  # noqa: PLW0603

        if self._ready_done:
            return

        try:
            registry = _build_registry()
            _REGISTRY_SINGLETON = registry

            tool_count = len(registry.list_tools())
            logger.info(
                "OrchestratorConfig.ready(): registered %d tools via ToolRegistry",
                tool_count,
            )
        except Exception:
            logger.exception(
                "OrchestratorConfig.ready(): failed to build ToolRegistry -- "
                "continuing without tools"
            )
        finally:
            OrchestratorConfig._ready_done = True
