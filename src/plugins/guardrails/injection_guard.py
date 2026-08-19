"""
Prompt Injection & Jailbreak Firewall Plugin ("Guardier Shield").
Detects and neutralizes adversarial prompt injection, system prompt extraction, and jailbreak attempts.
"""
import re
from typing import Dict, Any, Optional, List
from src.plugins.base import BaseGuardrailPlugin
from src.config import logger


class PromptInjectionGuardPlugin(BaseGuardrailPlugin):
    """Production-grade heuristic and pattern-matching prompt injection firewall."""

    # Adversarial patterns and jailbreak signatures
    INJECTION_PATTERNS = [
        # Instruction Overrides
        r"ignore\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts|rules|commands)",
        r"disregard\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts|rules|commands)",
        r"forget\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts|rules|commands)",
        r"bypass\s+(all\s+)?(security|guardrails|safety|rules|restrictions)",
        
        # System Prompt Extraction
        r"(show|tell|print|reveal|output|display|leak)\s+(me\s+)?(your\s+)?(system\s+prompt|initial\s+instructions|core\s+prompt)",
        r"what\s+are\s+your\s+(exact\s+)?(system\s+instructions|system\s+prompts|rules)",
        r"repeat\s+the\s+words\s+above",
        
        # Roleplay & Jailbreaks
        r"\b(dan|jailbreak|developer\s+mode|unfiltered\s+mode|god\s+mode)\b",
        r"you\s+are\s+now\s+(an\s+unfiltered|a\s+hacker|free\s+of\s+rules)",
        r"act\s+as\s+an\s+ai\s+without\s+(ethics|morals|rules|guardrails)",
        
        # Delimiter Escapes & Template Injections
        r"```\s*(system|assistant|admin)\s*",
        r"<\|im_start\|>",
        r"<\|im_end\|>",
        r"\[system\]",
        r"\[instruction\]",
    ]

    def __init__(self, sensitivity: float = 0.8):
        self.sensitivity = sensitivity
        self._compiled_patterns = [re.compile(p, re.IGNORECASE) for p in self.INJECTION_PATTERNS]

    @property
    def name(self) -> str:
        return "prompt_injection_guard"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Heuristic Prompt Injection & Jailbreak Defense Firewall."

    def evaluate_input(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Evaluates input query for prompt injection, jailbreak, or prompt leakage attempts."""
        if not text or not text.strip():
            return {"is_safe": True, "reason": "Empty text.", "threat_level": "none"}

        clean_text = text.strip()

        # 1. Pattern matching check
        for pattern in self._compiled_patterns:
            match = pattern.search(clean_text)
            if match:
                logger.warning(f"Security Alert: Blocked Prompt Injection attack matching '{match.group(0)}'")
                return {
                    "is_safe": False,
                    "reason": f"Prompt injection attempt detected: '{match.group(0)}'",
                    "threat_level": "high",
                    "attack_type": "instruction_override_or_leak",
                    "sanitized_text": "[Blocked Injection Attempt]",
                }

        # 2. Heuristic check: Excessive special characters / delimiter stacking
        special_char_ratio = len(re.findall(r"[<>{}\[\]|`\\]", clean_text)) / max(len(clean_text), 1)
        if special_char_ratio > 0.35 and len(clean_text) > 20:
            return {
                "is_safe": False,
                "reason": "Excessive delimiter characters detected (possible delimiter injection attack).",
                "threat_level": "medium",
                "attack_type": "delimiter_stacking",
                "sanitized_text": "[Blocked Delimiter Attack]",
            }

        return {
            "is_safe": True,
            "reason": "Clean input query.",
            "threat_level": "none",
            "sanitized_text": clean_text,
        }

    def evaluate_output(self, answer: str, context_chunks: List[Any]) -> Dict[str, Any]:
        """Checks if generated output inadvertently leaks system prompt tokens."""
        if not answer:
            return {"is_safe": True}

        leak_indicators = ["<|im_start|>", "[system]", "You are an enterprise AI assistant designed by"]
        for ind in leak_indicators:
            if ind.lower() in answer.lower():
                return {
                    "is_safe": False,
                    "reason": f"System prompt leakage token detected in answer: '{ind}'",
                }

        return {"is_safe": True, "reason": "No system prompt leakage detected."}
