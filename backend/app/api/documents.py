from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.audit_log import AuditLog
from app.models.document import Document, DocumentChunk
from app.models.user import User

router = APIRouter(prefix="/documents", tags=["documents"])


def log_audit(db: Session, user_id: int | None, action: str, resource: str, resource_id: str | None = None, metadata: dict | None = None):
    db.add(AuditLog(user_id=user_id, action=action, resource=resource, resource_id=resource_id, ip_address="127.0.0.1", metadata_json=metadata or {}))


@router.post("/upload")
def upload_document(file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    allowed = {"csv", "txt", "pdf", "docx"}
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Filename is required")
    ext = Path(file.filename).suffix.lower().lstrip('.')
    if ext not in allowed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type")
    content = file.file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File exceeds max upload size")
    import hashlib
    content_hash = hashlib.sha256(content).hexdigest()
    safe_name = f"{current_user.id}_{hashlib.sha256(file.filename.encode()).hexdigest()}.{ext}"
    document = Document(filename=safe_name, file_type=ext, uploaded_by=current_user.id, content_hash=content_hash, processing_status="processed")
    db.add(document); db.commit(); db.refresh(document)
    text = content.decode("utf-8", errors="replace")
    chunks = [text[i:i+250] for i in range(0, len(text), 250)]
    for idx, chunk in enumerate(chunks):
        db.add(DocumentChunk(document_id=document.id, chunk_text=chunk, chunk_index=idx, embedding_reference=f"chunk_{idx}"))
    db.commit()
    log_audit(db, current_user.id, "document_upload", "documents", str(document.id), {"filename": safe_name})
    return {"id": document.id, "filename": safe_name, "status": document.processing_status}


@router.get("")
def list_documents(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Document).all()


@router.delete("/{document_id}")
def delete_document(document_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    db.delete(document)
    db.commit()
    log_audit(db, current_user.id, "document_delete", "documents", str(document_id), {"status": "deleted"})
    return {"success": True, "deleted": document_id}
