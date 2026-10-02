import re
from typing import List

from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException


class PreprocessingService:
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()

    @staticmethod
    def clean_text(text: str) -> str:
        text = text.lower()
        text = re.sub(r"[^a-zA-Z0-9\s\-]", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    @staticmethod
    def detect_language(text: str) -> str:
        try:
            lang = detect(text)
            if lang == "ta":
                return "tamil"
            if lang == "en":
                return "english"
            return "tanglish / mixed"
        except LangDetectException:
            return "tanglish / mixed"

    @staticmethod
    def tokenize(text: str) -> List[str]:
        return [token for token in re.findall(r"\b\w+\b", text.lower()) if token]
