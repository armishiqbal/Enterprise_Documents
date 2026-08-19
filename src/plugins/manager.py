"""
Enterprise Plugin Manager and Registry for Document Intelligence Platform.
Provides thread-safe registration, discovery, lifecycle management, and execution pipelines.
"""
import threading
from typing import Dict, List, Any, Optional, Type
from src.plugins.base import (
    BasePlugin,
    PluginType,
    BaseConnectorPlugin,
    BaseEmbeddingPlugin,
    BaseGuardrailPlugin,
    BaseSecurityPlugin,
)
from src.config import logger


class PluginManager:
    """Thread-safe singleton registry for enterprise plugins."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(PluginManager, cls).__new__(cls)
                cls._instance._plugins: Dict[str, BasePlugin] = {}
                cls._instance._type_index: Dict[PluginType, List[str]] = {
                    pt: [] for pt in PluginType
                }
                cls._instance._active_embedding_plugin_name: Optional[str] = None
        return cls._instance

    def register_plugin(self, plugin: BasePlugin, config: Optional[Dict[str, Any]] = None) -> bool:
        """Registers a plugin instance and executes its initialization lifecycle hook."""
        with self._lock:
            name = plugin.name
            if name in self._plugins:
                logger.warning(f"Plugin '{name}' is already registered. Overwriting with new instance.")

            try:
                success = plugin.initialize(config)
                if not success:
                    logger.error(f"Plugin '{name}' failed during initialize() lifecycle.")
                    return False

                self._plugins[name] = plugin
                ptype = plugin.plugin_type
                if name not in self._type_index[ptype]:
                    self._type_index[ptype].append(name)

                if ptype == PluginType.EMBEDDING and self._active_embedding_plugin_name is None:
                    self._active_embedding_plugin_name = name

                logger.info(f"Registered plugin '{name}' v{plugin.version} [{ptype.value}]")
                return True
            except Exception as e:
                logger.error(f"Failed to register plugin '{name}': {e}")
                return False

    def unregister_plugin(self, plugin_name: str) -> bool:
        """Shuts down and unregisters a plugin by name."""
        with self._lock:
            if plugin_name not in self._plugins:
                return False
            plugin = self._plugins.pop(plugin_name)
            ptype = plugin.plugin_type
            if plugin_name in self._type_index[ptype]:
                self._type_index[ptype].remove(plugin_name)
            try:
                plugin.shutdown()
            except Exception as e:
                logger.warning(f"Error shutting down plugin '{plugin_name}': {e}")
            return True

    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """Retrieves a registered plugin by name."""
        return self._plugins.get(plugin_name)

    def list_plugins(self, plugin_type: Optional[PluginType] = None) -> List[Dict[str, Any]]:
        """Returns metadata list of all registered plugins, optionally filtered by type."""
        result = []
        for name, plugin in self._plugins.items():
            if plugin_type is None or plugin.plugin_type == plugin_type:
                result.append({
                    "name": plugin.name,
                    "version": plugin.version,
                    "type": plugin.plugin_type.value,
                    "description": plugin.description,
                })
        return result

    # --- Type-Specific Helpers ---

    def get_connector(self, name: str = "astra_connector") -> Optional[BaseConnectorPlugin]:
        """Retrieves a connector plugin (defaults to Astra connector)."""
        plugin = self.get_plugin(name)
        if isinstance(plugin, BaseConnectorPlugin):
            return plugin
        return None

    def get_embedding_plugin(self, name: Optional[str] = None) -> Optional[BaseEmbeddingPlugin]:
        """Retrieves the active or explicitly requested embedding plugin."""
        target_name = name or self._active_embedding_plugin_name
        if target_name and target_name in self._plugins:
            plugin = self._plugins[target_name]
            if isinstance(plugin, BaseEmbeddingPlugin):
                return plugin

        # Fallback to first available embedding plugin
        embed_plugins = self._type_index.get(PluginType.EMBEDDING, [])
        if embed_plugins:
            plugin = self._plugins[embed_plugins[0]]
            if isinstance(plugin, BaseEmbeddingPlugin):
                return plugin
        return None

    def set_active_embedding_plugin(self, name: str) -> bool:
        """Sets the active default embedding plugin by name."""
        with self._lock:
            if name in self._plugins and self._plugins[name].plugin_type == PluginType.EMBEDDING:
                self._active_embedding_plugin_name = name
                logger.info(f"Switched active embedding plugin to '{name}'.")
                return True
            logger.error(f"Embedding plugin '{name}' not found or invalid type.")
            return False

    def get_guardrail_plugins(self) -> List[BaseGuardrailPlugin]:
        """Retrieves all registered guardrail plugins."""
        names = self._type_index.get(PluginType.GUARDRAIL, [])
        return [self._plugins[n] for n in names if isinstance(self._plugins[n], BaseGuardrailPlugin)]

    def get_security_plugins(self) -> List[BaseSecurityPlugin]:
        """Retrieves all registered security plugins."""
        names = self._type_index.get(PluginType.SECURITY, [])
        return [self._plugins[n] for n in names if isinstance(self._plugins[n], BaseSecurityPlugin)]

    def run_input_guardrails(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Executes all registered input guardrails sequentially."""
        sanitized_query = query
        for guard in self.get_guardrail_plugins():
            eval_res = guard.evaluate_input(sanitized_query, context)
            if not eval_res.get("is_safe", True):
                return {
                    "is_safe": False,
                    "reason": eval_res.get("reason", "Blocked by security guardrail."),
                    "guardrail_name": guard.name,
                    "sanitized_query": sanitized_query,
                }
            if "sanitized_text" in eval_res:
                sanitized_query = eval_res["sanitized_text"]

        return {
            "is_safe": True,
            "reason": "All guardrails passed.",
            "guardrail_name": "none",
            "sanitized_query": sanitized_query,
        }

    def reset(self) -> None:
        """Clears all registered plugins (primarily for test teardown)."""
        with self._lock:
            for p in list(self._plugins.values()):
                try:
                    p.shutdown()
                except Exception:
                    pass
            self._plugins.clear()
            for pt in PluginType:
                self._type_index[pt].clear()
            self._active_embedding_plugin_name = None


# Global Plugin Manager Singleton
plugin_manager = PluginManager()
