from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.audit_log import AuditLog
from app.models.feedback import Feedback
from app.models.sentiment import SentimentResult
from app.schemas.sentiment import SentimentAnalyzeRequest, SentimentBatchRequest
from app.services.gemini_service import predict_sentiment_text

router = APIRouter(prefix="/sentiment", tags=["sentiment"])


def log_audit(db: Session, user_id: int | None, action: str, resource: str, resource_id: str | None = None, metadata: dict | None = None):
    db.add(AuditLog(user_id=user_id, action=action, resource=resource, resource_id=resource_id, ip_address="127.0.0.1", metadata_json=metadata or {}))


@router.post("/analyze")
def analyze(payload: SentimentAnalyzeRequest, current_user: object = Depends(get_current_user), db: Session = Depends(get_db)):
    if not payload.text.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Text cannot be empty")
    result = predict_sentiment_text(payload.text)
    feedback = Feedback(
        user_id=current_user.id,
        text=payload.text,
        language=result["language"],
        source=payload.source,
        category=payload.category or "general",
        department=payload.department or "general",
        product=payload.product or "general",
        location=payload.location or "unknown",
    )
    db.add(feedback); db.commit(); db.refresh(feedback)
    sentiment_record = SentimentResult(
        feedback_id=feedback.id,
        sentiment=result["sentiment"],
        confidence=result["confidence"],
        positive_score=result["positive_score"],
        negative_score=result["negative_score"],
        neutral_score=result["neutral_score"],
        model_name=settings.GEMINI_MODEL,
        model_version="gemini-generate-content",
    )
    db.add(sentiment_record)
    db.commit()
    log_audit(db, current_user.id, "sentiment_analysis", "sentiment_results", str(feedback.id), {"sentiment": result["sentiment"]})
    return {"feedback_id": feedback.id, "result": result}


@router.post("/batch")
def analyze_batch(payload: SentimentBatchRequest, current_user: object = Depends(get_current_user), db: Session = Depends(get_db)):
    results = []
    for item in payload.items:
        result = predict_sentiment_text(item.text)
        results.append({"text": item.text, "result": result})
    return {"count": len(results), "results": results}
