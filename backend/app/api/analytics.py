from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview")
def overview(db: Session = Depends(get_db), current_user: object = Depends(get_current_user)):
    return AnalyticsService.get_overview(db)


@router.get("/trends")
def trends(db: Session = Depends(get_db), current_user: object = Depends(get_current_user)):
    return AnalyticsService.get_trends(db)


@router.get("/categories")
def categories(db: Session = Depends(get_db), current_user: object = Depends(get_current_user)):
    return AnalyticsService.get_category_breakdown(db)
