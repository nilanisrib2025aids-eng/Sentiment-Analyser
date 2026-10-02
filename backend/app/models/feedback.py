from sqlalchemy import Column, DateTime, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    text = Column(Text, nullable=False)
    language = Column(String(50), nullable=False, default="en")
    source = Column(String(100), default="manual")
    category = Column(String(100), default="general")
    department = Column(String(100), default="general")
    product = Column(String(100), default="general")
    location = Column(String(100), default="unknown")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
    sentiment = relationship("SentimentResult", back_populates="feedback", uselist=False)
