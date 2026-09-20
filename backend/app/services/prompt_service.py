import os
from pathlib import Path
from app.core.config import settings

class PromptService:
    def __init__(self):
        self.prompts_dir = Path(__file__).resolve().parent.parent / "prompts"
        self._cache = {}

    def get_prompt(self, name: str, version: str = "v1") -> str:
        key = f"{name}_{version}"
        if key in self._cache:
            return self._cache[key]

        filename = f"{name}_{version}.txt"
        filepath = self.prompts_dir / filename

        if not filepath.exists():
            # Fallback to v1 if requested version not found
            filepath = self.prompts_dir / f"{name}_v1.txt"

        if filepath.exists():
            content = filepath.read_text(encoding="utf-8")
            self._cache[key] = content
            return content

        return f"You are VaaniCart AI shopping assistant. Help the user find products."

    def get_voice_prompt(self, version: str = None) -> str:
        ver = version or settings.PROMPT_VERSION_VOICE
        return self.get_prompt("voice_agent", ver)

    def get_intent_prompt(self, version: str = None) -> str:
        ver = version or settings.PROMPT_VERSION_INTENT
        return self.get_prompt("intent_classifier", ver)

    def get_comparison_prompt(self, version: str = "v1") -> str:
        return self.get_prompt("comparison", version)

    def get_rag_prompt(self, version: str = None) -> str:
        ver = version or settings.PROMPT_VERSION_RAG
        return self.get_prompt("rag_agent", ver)

prompt_service = PromptService()
