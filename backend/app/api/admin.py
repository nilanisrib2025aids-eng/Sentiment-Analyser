from fastapi import APIRouter, Depends

from app.core.config import settings
from app.core.security import require_roles
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/ai-status")
def ai_status(current_user: User = Depends(require_roles("ADMIN"))):
    return {
        "provider": "Google Gemini",
        "model": settings.GEMINI_MODEL,
        "configured": bool(settings.GEMINI_API_KEY.strip()),
    }
