import re
from typing import Dict, Any
from app.schemas.chat import SpokenOutput

class VoiceService:
    """
    Transforms backend responses into natural, euphonic Text-to-Speech (TTS) output.
    Cleans markdown, formats Indian Rupee symbols, and expands acronyms.
    """

    PRONUNCIATION_MAP = {
        r"\bANC\b": "Active Noise Cancellation",
        r"\bTWS\b": "True Wireless",
        r"\bGaN\b": "Gallium Nitride",
        r"\bOLED\b": "O-led",
        r"\bAMOLED\b": "Am-o-led",
        r"\bGPS\b": "G P S",
        r"\bSpO2\b": "blood oxygen",
        r"\bMRP\b": "M R P",
        r"\bUSB-C\b": "USB C",
        r"\bT-Shirt\b": "Tee Shirt",
        r"\bT-Shirts\b": "Tee Shirts",
        r"\b(\d+)mm\b": r"\1 millimeter",
        r"\b(\d+)L\b": r"\1 liter",
        r"\b(\d+)g\b": r"\1 grams"
    }

    @classmethod
    def clean_text_for_speech(cls, text: str) -> str:
        # 1. Remove markdown bold, italic, code backticks
        clean = re.sub(r"[\*\_`#]", "", text)
        
        # 2. Remove markdown links [text](url) -> text
        clean = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", clean)

        # 3. Format Currency: ₹2,499 or ₹2499 -> '2,499 rupees'
        clean = re.sub(r"₹\s*(\d+[\d,]*)", r"\1 rupees", clean)
        clean = re.sub(r"Rs\.?\s*(\d+[\d,]*)", r"\1 rupees", clean, flags=re.IGNORECASE)

        # 4. Expand tech acronyms
        for pattern, replacement in cls.PRONUNCIATION_MAP.items():
            clean = re.sub(pattern, replacement, clean)

        # 5. Remove bullet list markers at line start
        clean = re.sub(r"^\s*[\-\•\*\d+\.]\s*", "", clean, flags=re.MULTILINE)

        # 6. Normalize multiple spaces/newlines
        clean = re.sub(r"\s+", " ", clean).strip()

        return clean

    @classmethod
    def prepare_spoken_output(cls, raw_text: str, language_preference: str = "hinglish") -> SpokenOutput:
        speech_text = cls.clean_text_for_speech(raw_text)

        # Indian English voice code by default, or hi-IN for predominantly Hindi
        lang_code = "en-IN" if language_preference in ["en", "hinglish"] else "hi-IN"

        # SSML structure
        ssml = (
            f"<speak><p><s>{speech_text}</s></p></speak>"
        )

        return SpokenOutput(
            text=speech_text,
            ssml=ssml,
            language_code=lang_code,
            speech_rate=1.0
        )
