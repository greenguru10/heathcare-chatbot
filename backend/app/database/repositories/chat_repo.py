from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from backend.app.models.query import QueryRecord
from backend.app.models.answer import Answer
from backend.app.models.citation import Citation
from backend.app.models.feedback import Feedback
from backend.app.models.retrieval import RetrievalResult


class ChatRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_query_record(self, query_data: dict) -> QueryRecord:
        record = QueryRecord(**query_data)
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def save_retrieval_results(self, results: List[dict]):
        db_results = [RetrievalResult(**r) for r in results]
        self.db.add_all(db_results)
        self.db.commit()

    def save_answer(self, answer_data: dict) -> Answer:
        ans = Answer(**answer_data)
        self.db.add(ans)
        self.db.commit()
        self.db.refresh(ans)
        return ans

    def save_citations(self, citations_data: List[dict]) -> List[Citation]:
        citations = [Citation(**c) for c in citations_data]
        self.db.add_all(citations)
        self.db.commit()
        return citations

    def add_feedback(self, feedback_data: dict) -> Feedback:
        feedback = Feedback(**feedback_data)
        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)
        return feedback
