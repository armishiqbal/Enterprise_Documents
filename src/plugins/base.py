"""
Base Plugin Interfaces and Abstract Classes for Enterprise Document Intelligence Platform.
Defines standardized protocols for Connectors, Embedding Models, Guardrails, and Security engines.
"""
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Dict, Any, Optional


class PluginType(str, Enum):
    """Enumeration of supported plugin categories."""
    CONNECTOR = "connector"
    EMBEDDING = "embedding"
    GUARDRAIL = "guardrail"
    SECURITY = "security"
    VECTOR_STORE = "vector_store"


class BasePlugin(ABC):
    """Base interface that all enterprise plugins must implement."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier name of the plugin."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Version string of the plugin."""
        pass

    @property
    @abstractmethod
    def plugin_type(self) -> PluginType:
        """Category type of the plugin."""
        pass

    @property
    def description(self) -> str:
        """Human-readable description of plugin functionality."""
        return ""

    def initialize(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """Lifecycle hook called upon plugin registration/startup."""
        return True

    def shutdown(self) -> None:
        """Lifecycle hook called upon application shutdown."""
        pass

    def health_check(self) -> Dict[str, Any]:
        """Returns health and connectivity status of the plugin."""
        return {"status": "healthy", "plugin": self.name, "version": self.version}


class BaseConnectorPlugin(BasePlugin):
    """Base interface for external project connectors (e.g. Astra Project Connector)."""

    @property
    def plugin_type(self) -> PluginType:
        return PluginType.CONNECTOR

    @abstractmethod
    def delegate_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Delegates a search or analysis query to the external project service."""
        pass

    @abstractmethod
    def sync_documents(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synchronizes indexed documents and chunk metadata with the external service."""
        pass


class BaseEmbeddingPlugin(BasePlugin):
    """Base interface for multi-model embedding providers."""

    @property
    def plugin_type(self) -> PluginType:
        return PluginType.EMBEDDING

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Returns vector dimensionality produced by this embedding engine."""
        pass

    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generates high-dimensional embedding vectors for a list of texts."""
        pass

    @abstractmethod
    def embed_query(self, query: str) -> List[float]:
        """Generates embedding vector for a search query string."""
        pass


class BaseGuardrailPlugin(BasePlugin):
    """Base interface for prompt injection, toxicity, and factual guardrails."""

    @property
    def plugin_type(self) -> PluginType:
        return PluginType.GUARDRAIL

    @abstractmethod
    def evaluate_input(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Evaluates input query for safety, injection attempts, and domain compliance."""
        pass

    @abstractmethod
    def evaluate_output(self, answer: str, context_chunks: List[Any]) -> Dict[str, Any]:
        """Evaluates generated completion for factual grounding and data leakage."""
        pass


class BaseSecurityPlugin(BasePlugin):
    """Base interface for PII redaction, RBAC, and Audit Logging."""

    @property
    def plugin_type(self) -> PluginType:
        return PluginType.SECURITY

    @abstractmethod
    def process_security(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Processes payload through security rules (redaction, access check, or auditing)."""
        pass
