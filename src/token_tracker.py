"""
Token tracking, tiktoken token counting, and API cost estimation engine.
"""
from typing import Dict, Any


class TokenTracker:
    """Calculates token counts and estimates LLM query costs."""

    # Pricing rates per 1,000,000 tokens (USD)
    PRICING_TABLE = {
        "gpt-4o-mini": {"prompt": 0.15, "completion": 0.60},
        "gpt-4o": {"prompt": 2.50, "completion": 10.00},
        "o3-mini": {"prompt": 1.10, "completion": 4.40},
        "o1-mini": {"prompt": 3.00, "completion": 12.00},
        "gpt-3.5-turbo": {"prompt": 0.50, "completion": 1.50},
        "llama-3.3-70b-versatile": {"prompt": 0.59, "completion": 0.79},
        "openai/gpt-oss-120b": {"prompt": 0.49, "completion": 0.69},
        "openai/gpt-oss-20b": {"prompt": 0.10, "completion": 0.15},
        "qwen/qwen3.6-27b": {"prompt": 0.20, "completion": 0.30},
        "deepseek-r1-distill-llama-70b": {"prompt": 0.59, "completion": 0.79},
        "llama-3.1-8b-instant": {"prompt": 0.05, "completion": 0.08},
        "mixtral-8x7b-32768": {"prompt": 0.24, "completion": 0.24},
        "gemma2-9b-it": {"prompt": 0.20, "completion": 0.20},
        "default": {"prompt": 0.15, "completion": 0.60},
    }

    @classmethod
    def count_tokens(cls, text: str, model_name: str = "gpt-4o-mini") -> int:
        """Counts tokens in a string using tiktoken."""
        if not text:
            return 0
        try:
            import tiktoken
            encoding = tiktoken.encoding_for_model(model_name)
            return len(encoding.encode(text))
        except Exception:
            # Fallback estimation: average ~4 characters per token in English
            return max(1, len(text) // 4)

    @classmethod
    def estimate_cost(
        cls, prompt_tokens: int, completion_tokens: int, model_name: str = "gpt-4o-mini"
    ) -> float:
        """Estimates total cost in USD based on prompt and completion tokens."""
        pricing = cls.PRICING_TABLE.get(model_name, cls.PRICING_TABLE["default"])
        prompt_cost = (prompt_tokens / 1_000_000.0) * pricing["prompt"]
        completion_cost = (completion_tokens / 1_000_000.0) * pricing["completion"]
        return round(prompt_cost + completion_cost, 6)


class TokenSession:
    """Session tracker maintaining cumulative token usage and cost metrics."""

    def __init__(self):
        self.total_prompt_tokens: int = 0
        self.total_completion_tokens: int = 0
        self.total_queries: int = 0
        self.total_cost_usd: float = 0.0

    def add_query_usage(
        self, prompt_text: str, completion_text: str, model_name: str = "gpt-4o-mini"
    ) -> Dict[str, Any]:
        """Tracks usage for a single query and updates cumulative session metrics."""
        p_tokens = TokenTracker.count_tokens(prompt_text, model_name)
        c_tokens = TokenTracker.count_tokens(completion_text, model_name)
        cost = TokenTracker.estimate_cost(p_tokens, c_tokens, model_name)

        self.total_prompt_tokens += p_tokens
        self.total_completion_tokens += c_tokens
        self.total_queries += 1
        self.total_cost_usd += cost

        return {
            "prompt_tokens": p_tokens,
            "completion_tokens": c_tokens,
            "total_tokens": p_tokens + c_tokens,
            "cost_usd": cost,
            "session_total_tokens": self.total_prompt_tokens + self.total_completion_tokens,
            "session_total_cost_usd": round(self.total_cost_usd, 6),
        }

    def get_summary(self) -> Dict[str, Any]:
        """Returns session usage metrics summary."""
        return {
            "total_queries": self.total_queries,
            "total_prompt_tokens": self.total_prompt_tokens,
            "total_completion_tokens": self.total_completion_tokens,
            "total_tokens": self.total_prompt_tokens + self.total_completion_tokens,
            "total_cost_usd": round(self.total_cost_usd, 6),
            "formatted_cost": f"${self.total_cost_usd:.5f}",
        }
