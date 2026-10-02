from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.audit_log import AuditLog
from app.models.feedback import Feedback
from app.models.sentiment import SentimentResult
from app.schemas.feedback import FeedbackCreate, FeedbackOut

router = APIRouter(prefix="/feedback", tags=["feedback"])


def log_audit(db: Session, user_id: int | None, action: str, resource: str, resource_id: str | None = None, metadata: dict | None = None):
    db.add(AuditLog(user_id=user_id, action=action, resource=resource, resource_id=resource_id, ip_address="127.0.0.1", metadata_json=metadata or {}))


@router.post("", response_model=FeedbackOut)
def create_feedback(payload: FeedbackCreate, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    feedback = Feedback(
        user_id=current_user.id,
        text=payload.text,
        language=payload.language or "en",
        source=payload.source,
        category=payload.category,
        department=payload.department,
        product=payload.product,
        location=payload.location,
    )
    db.add(feedback)
    db.commit(); db.refresh(feedback)
    log_audit(db, current_user.id, "feedback_creation", "feedback", str(feedback.id), {"source": payload.source})
    return feedback


@router.get("", response_model=list[FeedbackOut])
def list_feedback(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user), skip: int = 0, limit: int = 50):
    return db.query(Feedback).offset(skip).limit(limit).all()


@router.get("/{feedback_id}")
def get_feedback(feedback_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not feedback:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")
    sentiment = db.query(SentimentResult).filter(SentimentResult.feedback_id == feedback.id).first()
    return {
        "feedback": feedback,
        "sentiment": sentiment,
    }
