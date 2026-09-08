import uuid
import time
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.app.schemas.chat import ChatRequest, ChatResponse
from backend.app.core.constants import RiskLevel, SafetyRoute, ResponseMode
from backend.app.core.privacy import redact_sensitive_content
from backend.app.safety.triage import route_health_query
from backend.app.safety.emergency import build_emergency_response, build_blocked_response
from backend.app.nlp.normalizer import normalize_query
from backend.app.nlp.intent import intent_classifier
from backend.app.nlp.entities import entity_extractor
from backend.app.conversation.state import HealthcareConversationState, resolver
from backend.app.conversation.privacy_context import build_safe_context_summary
from backend.app.retrieval.retriever import retriever
from backend.app.retrieval.index_manager import index_manager
from backend.app.generation.prompt_builder import prompt_builder
from backend.app.generation.llm_gateway import llm_client, get_llm_client
from backend.app.generation.citation_validator import citation_validator
from backend.app.generation.grounding_validator import grounding_validator
from backend.app.generation.output_safety_validator import output_safety_validator
from backend.app.generation.confidence import calculate_confidence
from backend.app.generation.response_builder import response_builder
from backend.app.database.repositories.session_repo import SessionRepository
from backend.app.database.repositories.chat_repo import ChatRepository
from backend.app.database.repositories.audit_repo import AuditRepository
from backend.app.core.logging import logger


class ChatService:
    def __init__(self, db: Session):
        self.db = db
        self.session_repo = SessionRepository(db)
        self.chat_repo = ChatRepository(db)
        self.audit_repo = AuditRepository(db)

    async def answer(self, request: ChatRequest, request_id: Optional[str] = None) -> ChatResponse:
        start_time = time.perf_counter()
        req_id = request_id or f"req_{uuid.uuid4().hex[:8]}"
        raw_message = request.message.strip()

        # 1. Privacy Minimization & Normalization
        minimized_query = redact_sensitive_content(raw_message)
        normalized_q = normalize_query(minimized_query)

        # 2. Safety Gate Assessment (Deterministic)
        safety_route, risk_level, safety_reason = route_health_query(raw_message)
        
        # Ensure session exists
        session = self.session_repo.get_or_create_session(request.session_id)
        session_id = session.id

        # Save user message to session
        self.session_repo.add_message(
            session_id=session_id,
            role="user",
            content=minimized_query,
            metadata={"risk_level": risk_level.value, "route": safety_route.value}
        )

        # Emergency / Crisis Route -> Immediately Return Safe Guidance (No LLM, No Retrieval)
        if safety_route in (SafetyRoute.EMERGENCY, SafetyRoute.CRISIS):
            emergency_payload = build_emergency_response(
                region=request.locale.split("-")[-1] if request.locale else "IN",
                is_crisis=(safety_route == SafetyRoute.CRISIS)
            )
            response = response_builder.build_grounded_response(
                request_id=req_id,
                session_id=session_id,
                parsed_llm_json=emergency_payload,
                evidence_items=[],
                confidence_score=1.0,
                confidence_label="high",
                confidence_explanation="Deterministic emergency safety protocol activated.",
                risk_level=risk_level,
                follow_up_suggestions=[]
            )
            self._persist_chat_turn(session_id, req_id, minimized_query, normalized_q, "emergency", risk_level, response, [])
            return response

        # Blocked Prescriptive / Diagnosis Route -> Immediately Return Refusal
        if safety_route in (SafetyRoute.BLOCKED_MEDICATION_ADVICE, SafetyRoute.DIAGNOSIS_DEFERRAL):
            blocked_payload = build_blocked_response(safety_route.value)
            response = response_builder.build_grounded_response(
                request_id=req_id,
                session_id=session_id,
                parsed_llm_json=blocked_payload,
                evidence_items=[],
                confidence_score=1.0,
                confidence_label="high",
                confidence_explanation="Deterministic safety boundary enforced.",
                risk_level=risk_level,
                follow_up_suggestions=blocked_payload.get("follow_up_suggestions", [])
            )
            self._persist_chat_turn(session_id, req_id, minimized_query, normalized_q, safety_route.value, risk_level, response, [])
            return response

        # 3. Follow-Up Resolution & Intent Classification
        state_dict = session.state_json or {}
        conv_state = HealthcareConversationState(
            session_id=session_id,
            previous_topics=state_dict.get("previous_topics", []),
            previous_intent=state_dict.get("previous_intent")
        )
        resolved_query = resolver.resolve_follow_up(normalized_q, conv_state)
        intent, intent_conf = intent_classifier.classify(resolved_query)

        # 4. Hybrid Retrieval
        retrieval_res = retriever.retrieve(resolved_query)
        evidence_chunks = retrieval_res["evidence_chunks"]

        # If index empty or no evidence returned -> Safe Abstention
        if not evidence_chunks:
            abstain_json = {
                "answer": "I do not have enough verified information in the approved knowledge base to answer that safely.",
                "key_points": [],
                "when_to_seek_care": "For specific symptoms or medical advice, please consult a qualified healthcare professional.",
                "limitations": "Educational healthcare assistant with curated source grounding.",
                "used_source_ids": [],
                "uncertainty": "high"
            }
            response = response_builder.build_grounded_response(
                request_id=req_id,
                session_id=session_id,
                parsed_llm_json=abstain_json,
                evidence_items=[],
                confidence_score=0.35,
                confidence_label="insufficient",
                confidence_explanation="No verified evidence was found in the approved corpus.",
                risk_level=risk_level,
                follow_up_suggestions=["What other health topics are available?"]
            )
            self._persist_chat_turn(session_id, req_id, minimized_query, normalized_q, intent, risk_level, response, [])
            return response

        # 5. Build Guarded Prompt & Call LLM Gateway
        session_messages = [{"role": m.role, "content": m.content} for m in session.messages]
        safe_summary = build_safe_context_summary(session_messages)
        user_prompt = prompt_builder.build_user_prompt(resolved_query, evidence_chunks, safe_summary)

        active_llm = get_llm_client()
        llm_gen = await active_llm.generate_grounded_answer(
            system_prompt=prompt_builder.system_prompt,
            user_prompt=user_prompt
        )

        parsed_json = llm_gen.parsed_json
        answer_text = parsed_json.get("answer", "")

        # 6. Verification Layers
        # Citation check
        is_cit_valid, cit_errors, cit_meta = citation_validator.validate_citations(answer_text, evidence_chunks)
        # Grounding check
        is_grounded, grounding_score, unsupp = grounding_validator.validate_grounding(answer_text, evidence_chunks)
        # Output safety check
        is_out_safe, out_errors = output_safety_validator.validate_output(answer_text)

        # If output contains dangerous diagnosis/prescriptions -> Reject & fallback to safe refusal
        if not is_out_safe:
            refusal_payload = build_blocked_response("output_safety_violation")
            response = response_builder.build_grounded_response(
                request_id=req_id,
                session_id=session_id,
                parsed_llm_json=refusal_payload,
                evidence_items=[],
                confidence_score=0.90,
                confidence_label="high",
                confidence_explanation="Output filtered by medical safety guardrails.",
                risk_level=RiskLevel.BLOCKED
            )
            self._persist_chat_turn(session_id, req_id, minimized_query, normalized_q, intent, RiskLevel.BLOCKED, response, evidence_chunks)
            return response

        # 7. Confidence Calculation
        conf_score, conf_label, conf_exp = calculate_confidence(
            retrieval_evidence=evidence_chunks,
            grounding_score=grounding_score,
            intent_confidence=intent_conf
        )

        # 8. Assemble Final Response
        response = response_builder.build_grounded_response(
            request_id=req_id,
            session_id=session_id,
            parsed_llm_json=parsed_json,
            evidence_items=evidence_chunks,
            confidence_score=conf_score,
            confidence_label=conf_label,
            confidence_explanation=conf_exp,
            risk_level=risk_level,
            follow_up_suggestions=[
                "What other preventive steps can I take?",
                "When should I speak with a healthcare provider?"
            ]
        )

        # 9. Update Session State & Persist Turn
        topics = state_dict.get("previous_topics", [])
        if evidence_chunks:
            main_topic = evidence_chunks[0]["chunk"].get("title", intent)
            topics.append(main_topic)
            
        session_title = state_dict.get("title")
        if not session_title:
            clean_q = minimized_query.strip()
            session_title = clean_q[:35] + "..." if len(clean_q) > 35 else clean_q

        self.session_repo.update_session_state(session_id, {
            "title": session_title,
            "previous_topics": topics[-5:],
            "previous_intent": intent,
            "previous_risk_level": risk_level.value
        })

        self._persist_chat_turn(session_id, req_id, minimized_query, normalized_q, intent, risk_level, response, evidence_chunks)
        return response

    def _persist_chat_turn(
        self,
        session_id: str,
        request_id: str,
        raw_query: str,
        normalized_query: str,
        intent: str,
        risk_level: RiskLevel,
        response: ChatResponse,
        evidence_chunks: list
    ):
        try:
            # Query Record
            q_record = self.chat_repo.save_query_record({
                "session_id": session_id,
                "raw_query": raw_query,
                "normalized_query": normalized_query,
                "intent": intent,
                "risk_level": risk_level.value,
                "intent_confidence": 1.0
            })

            # Answer Record
            answer_record = self.chat_repo.save_answer({
                "query_id": q_record.id,
                "model_provider": "grounded_rag",
                "model_name": "rag_v1",
                "response_mode": response.response_mode.value,
                "answer_text": response.answer,
                "key_points_json": response.key_points,
                "when_to_seek_care": response.when_to_seek_care,
                "limitations": response.limitations,
                "confidence_score": response.confidence.score,
                "confidence_label": response.confidence.label,
                "confidence_explanation": response.confidence.explanation,
                "grounding_score": 1.0,
                "safety_flags": [risk_level.value]
            })

            # Save assistant message to session with full structured payload
            msg_metadata = {
                "answer_id": answer_record.id,
                "response_mode": response.response_mode.value,
                "risk_level": response.risk_level.value,
                "key_points": response.key_points,
                "when_to_seek_care": response.when_to_seek_care,
                "limitations": response.limitations,
                "confidence": response.confidence.model_dump() if response.confidence else None,
                "sources": [s.model_dump() for s in (response.sources or [])],
                "follow_up_suggestions": response.follow_up_suggestions
            }
            self.session_repo.add_message(
                session_id=session_id,
                role="assistant",
                content=response.answer,
                metadata=msg_metadata
            )

            # Citations
            if response.sources and evidence_chunks:
                citations_data = []
                for i, src in enumerate(response.sources):
                    if i < len(evidence_chunks):
                        chunk_id = evidence_chunks[i]["chunk"]["chunk_id"]
                        citations_data.append({
                            "answer_id": answer_record.id,
                            "chunk_id": chunk_id,
                            "citation_key": src.citation_key,
                            "excerpt": src.excerpt,
                            "citation_order": i + 1
                        })
                if citations_data:
                    self.chat_repo.save_citations(citations_data)

            # Audit Event
            self.audit_repo.log_event(
                event_type="chat.query_processed",
                request_id=request_id,
                metadata={
                    "risk_level": risk_level.value,
                    "response_mode": response.response_mode.value,
                    "evidence_count": len(evidence_chunks),
                    "confidence_score": response.confidence.score
                }
            )
        except Exception as e:
            logger.error("Failed to persist chat turn audit record", error=str(e))
