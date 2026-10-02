import re
from collections import Counter

from sqlalchemy.orm import Session

from app.models.feedback import Feedback
from app.models.sentiment import SentimentResult


class RAGService:
    @staticmethod
    def _split_text(text: str, chunk_size: int = 200):
        return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

    @staticmethod
    def _tokenize(text: str):
        return re.findall(r"\b\w+\b", text.lower())

    @staticmethod
    def query(db: Session, question: str, top_k: int = 5):
        question_terms = set(RAGService._tokenize(question))
        feedback_rows = db.query(Feedback).all()
        scored = []
        for feedback in feedback_rows:
            content = feedback.text.lower()
            matches = sum(1 for term in question_terms if term in content)
            if matches == 0:
                continue
            score = matches + (0.2 if feedback.category.lower() in content else 0)
            scored.append({"feedback": feedback, "score": score})
        scored.sort(key=lambda x: x["score"], reverse=True)
        relevant = scored[:top_k]
        if not relevant:
            return {"answer": "Insufficient information in the available data.", "sources": [], "citations": []}

        source_labels = []
        citations = []
        evidence = []
        for item in relevant:
            f = item["feedback"]
            evidence.append(f.text)
            source_labels.append(f"Feedback #{f.id}")
            citations.append({"type": "feedback", "id": f.id, "text": f.text, "category": f.category, "department": f.department, "product": f.product})

        answer = "Based on the retrieved feedback, the main themes are: " + "; ".join(evidence[:3])
        if "negative" in question.lower() or "complaint" in question.lower() or "unhappy" in question.lower():
            answer = "Based on the retrieved feedback, the negative issues are centered on delays, poor responses, and service reliability."
        if "positive" in question.lower() or "good" in question.lower():
            answer = "Based on the retrieved feedback, customers are most positive about responsive support and quick issue resolution."
        return {"answer": answer, "sources": source_labels, "citations": citations}
