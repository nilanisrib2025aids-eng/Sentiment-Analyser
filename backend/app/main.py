from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect

from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.core.security import get_password_hash
from app.models.audit_log import AuditLog
from app.models.feedback import Feedback
from app.models.sentiment import SentimentResult
from app.models.user import User
from app.models.document import Document, DocumentChunk

from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.feedback import router as feedback_router
from app.api.sentiment import router as sentiment_router
from app.api.analytics import router as analytics_router
from app.api.rag import router as rag_router
from app.api.documents import router as documents_router
from app.api.admin import router as admin_router

app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0", docs_url="/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(users_router, prefix=settings.API_V1_STR)
app.include_router(feedback_router, prefix=settings.API_V1_STR)
app.include_router(sentiment_router, prefix=settings.API_V1_STR)
app.include_router(analytics_router, prefix=settings.API_V1_STR)
app.include_router(rag_router, prefix=settings.API_V1_STR)
app.include_router(documents_router, prefix=settings.API_V1_STR)
app.include_router(admin_router, prefix=settings.API_V1_STR)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    seed_demo_data()


def seed_demo_data():
    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            admin = User(
                name="Admin User",
                email="admin@sih.local",
                password_hash=get_password_hash("Admin@123"),
                role="ADMIN",
                is_active=True,
            )
            analyst = User(
                name="Analyst User",
                email="analyst@sih.local",
                password_hash=get_password_hash("Analyst@123"),
                role="ANALYST",
                is_active=True,
            )
            user = User(
                name="Regular User",
                email="user@sih.local",
                password_hash=get_password_hash("User@123"),
                role="USER",
                is_active=True,
            )
            db.add_all([admin, analyst, user])
            db.commit()

        if db.query(Feedback).count() == 0:
            sample_feedback = [
                {"text": "Customer service was excellent and the issue was resolved quickly.", "language": "en", "source": "survey", "category": "support", "department": "customer_service", "product": "mobile_app", "location": "chennai", "user_id": 1},
                {"text": "The delivery was extremely late and nobody responded to my complaint.", "language": "en", "source": "review", "category": "delivery", "department": "logistics", "product": "ecommerce", "location": "bangalore", "user_id": 1},
                {"text": "The product was delivered yesterday.", "language": "en", "source": "portal", "category": "product", "department": "sales", "product": "device", "location": "hyderabad", "user_id": 1},
                {"text": "Service romba nalla iruku and support team solved my issue.", "language": "tanglish", "source": "chat", "category": "support", "department": "customer_service", "product": "service", "location": "madurai", "user_id": 2},
                {"text": "Delivery was delayed and support never replied for days.", "language": "en", "source": "complaint", "category": "delivery", "department": "logistics", "product": "shipping", "location": "coimbatore", "user_id": 2},
                {"text": "The interface is okay but the app crashes sometimes.", "language": "en", "source": "review", "category": "product", "department": "product_team", "product": "mobile_app", "location": "pune", "user_id": 3},
            ]
            for item in sample_feedback:
                db.add(Feedback(**item))
            db.commit()

        if db.query(AuditLog).count() == 0:
            db.add(AuditLog(user_id=1, action="system_init", resource="platform", resource_id="seed", ip_address="127.0.0.1", metadata_json={"note": "Synthetic demo data loaded"}))
            db.commit()
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "Sentiment Intelligence Platform API is running"}
