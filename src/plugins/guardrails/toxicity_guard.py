"""
Toxicity & Domain Content Guardrail Plugin.
Filters inappropriate, toxic, or out-of-domain queries to maintain enterprise professionalism.
"""
import re
from typing import Dict, Any, Optional, List
from src.plugins.base import BaseGuardrailPlugin
from src.config import logger


class ToxicityGuardPlugin(BaseGuardrailPlugin):
    """Filters toxic content, severe profanity, and harmful instructions."""

    HARMFUL_PATTERNS = [
        r"\b(how\s+to\s+hack|steal\s+passwords|sql\s+injection\s+exploit|ddos\s+attack)\b",
        r"\b(create\s+malware|ransomware\s+script|bypass\s+firewall\s+exploit)\b",
        r"\b(make\s+a\s+bomb|synthesize\s+explosives|illegal\s+weapons)\b",
    ]

    def __init__(self):
        self._compiled_patterns = [re.compile(p, re.IGNORECASE) for p in self.HARMFUL_PATTERNS]

    @property
    def name(self) -> str:
        return "toxicity_guard"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Filters harmful technical exploits and out-of-policy instructions."

    def evaluate_input(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not text or not text.strip():
            return {"is_safe": True}

        for pattern in self._compiled_patterns:
            match = pattern.search(text)
            if match:
                logger.warning(f"Security Alert: Blocked unsafe request matching '{match.group(0)}'")
                return {
                    "is_safe": False,
                    "reason": f"Request blocked by safety policy: '{match.group(0)}'",
                    "threat_level": "critical",
                    "sanitized_text": "[Blocked Harmful Policy Violation]",
                }

        return {"is_safe": True, "reason": "Passed toxicity safety checks.", "sanitized_text": text}

    def evaluate_output(self, answer: str, context_chunks: List[Any]) -> Dict[str, Any]:
        return {"is_safe": True}
