from typing import Dict, Any, List
from backend.app.schemas.chat import ChatResponse, SourceCitationResponse, ConfidenceResponse
from backend.app.core.constants import RiskLevel, ResponseMode


class ResponseBuilder:
    def build_grounded_response(
        self,
        request_id: str,
        session_id: str,
        parsed_llm_json: Dict[str, Any],
        evidence_items: List[Dict[str, Any]],
        confidence_score: float,
        confidence_label: str,
        confidence_explanation: str,
        risk_level: RiskLevel,
        follow_up_suggestions: List[str] = None
    ) -> ChatResponse:
        sources_list: List[SourceCitationResponse] = []
        for i, item in enumerate(evidence_items):
            chunk = item["chunk"]
            citation_key = f"S{i+1}"
            
            # Format excerpt
            raw_text = chunk.get("raw_text", "")
            excerpt = raw_text[:280] + "..." if len(raw_text) > 280 else raw_text

            sources_list.append(SourceCitationResponse(
                citation_key=citation_key,
                title=chunk.get("title", "Authoritative Source"),
                source_name=chunk.get("source_name", "Public Health Authority"),
                authority_tier=chunk.get("authority_tier", "A"),
                section=chunk.get("section", "General"),
                publication_date=chunk.get("publication_date"),
                last_updated=chunk.get("last_updated"),
                url=chunk.get("source_url"),
                excerpt=excerpt
            ))

        resp_mode = parsed_llm_json.get("response_mode", ResponseMode.GROUNDED_ANSWER)

        return ChatResponse(
            request_id=request_id,
            session_id=session_id,
            response_mode=resp_mode,
            risk_level=risk_level,
            answer=parsed_llm_json.get("answer", ""),
            key_points=parsed_llm_json.get("key_points", []),
            when_to_seek_care=parsed_llm_json.get("when_to_seek_care"),
            limitations=parsed_llm_json.get("limitations", "Educational information only; not medical advice or diagnosis."),
            confidence=ConfidenceResponse(
                score=confidence_score,
                label=confidence_label,
                explanation=confidence_explanation
            ),
            sources=sources_list,
            follow_up_suggestions=follow_up_suggestions or [
                "What are general ways to reduce risk?",
                "When should I speak with a healthcare professional?"
            ]
        )


response_builder = ResponseBuilder()
