from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.rag import RAGAnswer, RAGQueryRequest
from app.services.rag_service import RAGService

router = APIRouter(prefix="/rag", tags=["rag"])


def log_audit(db: Session, user_id: int | None, action: str, resource: str, resource_id: str | None = None, metadata: dict | None = None):
    db.add(AuditLog(user_id=user_id, action=action, resource=resource, resource_id=resource_id, ip_address="127.0.0.1", metadata_json=metadata or {}))


@router.post("/query", response_model=RAGAnswer)
def query(payload: RAGQueryRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    result = RAGService.query(db, payload.question, top_k=payload.top_k)
    log_audit(db, current_user.id, "rag_query", "rag", None, {"question": payload.question[:200]})
    db.commit()
    return result
