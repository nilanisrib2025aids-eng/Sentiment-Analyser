from collections import Counter
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.feedback import Feedback
from app.models.sentiment import SentimentResult


class AnalyticsService:
    @staticmethod
    def get_overview(db: Session):
        total = db.query(Feedback).count()
        sentiment_counts = {
            "positive": 0,
            "negative": 0,
            "neutral": 0,
        }
        avg_confidence = 0.0
        sentiment_rows = db.query(SentimentResult).all()
        for row in sentiment_rows:
            key = row.sentiment.lower()
            if key in sentiment_counts:
                sentiment_counts[key] += 1
            avg_confidence += row.confidence
        if sentiment_rows:
            avg_confidence = avg_confidence / len(sentiment_rows)
        return {
            "total_feedback": total,
            "positive_percentage": round((sentiment_counts["positive"] / total * 100), 2) if total else 0,
            "negative_percentage": round((sentiment_counts["negative"] / total * 100), 2) if total else 0,
            "neutral_percentage": round((sentiment_counts["neutral"] / total * 100), 2) if total else 0,
            "average_confidence": round(avg_confidence, 4),
            "processed_today": 0,
        }

    @staticmethod
    def get_trends(db: Session):
        rows = db.query(Feedback, SentimentResult).join(SentimentResult, SentimentResult.feedback_id == Feedback.id).all()
        trend = {}
        for feedback, result in rows:
            day = feedback.created_at.date().isoformat()
            trend.setdefault(day, {"positive": 0, "negative": 0, "neutral": 0})
            trend[day][result.sentiment.lower()] += 1
        return [{"date": day, "positive": val["positive"], "negative": val["negative"], "neutral": val["neutral"]} for day, val in sorted(trend.items())]

    @staticmethod
    def get_category_breakdown(db: Session):
        rows = db.query(Feedback, SentimentResult).join(SentimentResult, SentimentResult.feedback_id == Feedback.id).all()
        counts = Counter()
        for feedback, result in rows:
            counts[(feedback.category, result.sentiment.lower())] += 1
        result = []
        for (category, sentiment), count in counts.items():
            result.append({"category": category, "sentiment": sentiment, "count": count})
        return result
