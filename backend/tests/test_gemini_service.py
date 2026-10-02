import json

import httpx
import pytest
from fastapi import HTTPException

from app.core.config import settings
from app.services import gemini_service


def test_predict_sentiment_uses_gemini_response(monkeypatch):
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "test-key")
    analysis = {
        "sentiment": "negative",
        "confidence": 0.94,
        "positive_score": 0.02,
        "negative_score": 0.94,
        "neutral_score": 0.04,
        "language": "English",
        "explanation": "The customer says the service was not good.",
        "important_keywords": ["not good", "service"],
    }
    request = {}

    def fake_post(url, **kwargs):
        request["url"] = url
        request.update(kwargs)
        return httpx.Response(200, json={"candidates": [{"content": {"parts": [{"text": json.dumps(analysis)}]}}]})

    monkeypatch.setattr(gemini_service.httpx, "post", fake_post)

    result = gemini_service.predict_sentiment_text("The service was not good.")

    assert result == analysis
    assert request["headers"]["x-goog-api-key"] == "test-key"
    assert request["url"].endswith(f"/models/{settings.GEMINI_MODEL}:generateContent")
    assert request["json"]["contents"][0]["parts"][0]["text"] == "The service was not good."


def test_predict_sentiment_requires_gemini_key(monkeypatch):
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "")

    with pytest.raises(HTTPException) as error:
        gemini_service.predict_sentiment_text("not good")

    assert error.value.status_code == 503
    assert "GEMINI_API_KEY" in error.value.detail


def test_provider_error_is_reported_without_exposing_key(monkeypatch):
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "test-secret")
    monkeypatch.setattr(
        gemini_service.httpx,
        "post",
        lambda *args, **kwargs: httpx.Response(
            403,
            json={"error": {"message": "Gemini API access denied; test-secret"}},
        ),
    )

    with pytest.raises(HTTPException) as error:
        gemini_service.predict_sentiment_text("not good")

    assert error.value.status_code == 502
    assert "access denied" in error.value.detail
    assert "test-secret" not in error.value.detail