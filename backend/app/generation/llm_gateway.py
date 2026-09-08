import json
import re
from typing import Dict, Any, List, Optional, Protocol
from dataclasses import dataclass, field
import httpx
from backend.app.core.config import settings
from backend.app.core.exceptions import LLMGatewayException


@dataclass
class LLMGenerationResult:
    raw_output: str
    parsed_json: Dict[str, Any]
    model_provider: str
    model_name: str
    token_usage: Dict[str, int] = field(default_factory=dict)


class LLMClient(Protocol):
    async def generate_grounded_answer(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 700,
    ) -> LLMGenerationResult:
        ...


class MockGroundedClient:
    """
    Deterministic offline client for test environments and zero-API-key setups.
    Synthesizes answers directly from the evidence passed in the user prompt.
    """
    async def generate_grounded_answer(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 700,
    ) -> LLMGenerationResult:
        # Extract evidence blocks [S1], [S2], etc. from prompt
        evidence_matches = re.findall(r"\[(S\d+)\]\s*Title:\s*(.*?)\nAuthority:\s*(.*?)\nSection:\s*(.*?)\nDate:\s*(.*?)\nText:\s*(.*?)(?=\n\[S\d+\]|\nINSTRUCTIONS:|$)", user_prompt, re.DOTALL)
        
        if not evidence_matches:
            fallback = {
                "answer": "I do not have enough verified information in the approved knowledge base to answer that safely.",
                "key_points": [],
                "when_to_seek_care": "For medical concerns or clinical symptoms, consult a qualified healthcare professional.",
                "limitations": "Educational healthcare information only; not personal medical advice.",
                "used_source_ids": [],
                "uncertainty": "high"
            }
            return LLMGenerationResult(
                raw_output=json.dumps(fallback),
                parsed_json=fallback,
                model_provider="mock",
                model_name="mock-grounded-v1",
                token_usage={"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150}
            )

        # Synthesize concise grounded answer from top evidence chunks
        key_points = []
        used_ids = []
        answer_parts = []

        for match in evidence_matches[:3]:
            s_id = match[0]
            title = match[1].strip()
            section = match[3].strip()
            text = match[5].strip()
            
            # Grab first 2 clean sentences from chunk
            sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) > 15]
            if sentences:
                main_sentence = sentences[0]
                answer_parts.append(f"{main_sentence} [{s_id}]")
                if len(sentences) > 1:
                    key_points.append(f"{sentences[1]} [{s_id}]")
                else:
                    key_points.append(f"Derived from {title} ({section}). [{s_id}]")
                used_ids.append(s_id)

        answer_text = " ".join(answer_parts)
        
        parsed = {
            "answer": answer_text,
            "key_points": key_points[:3],
            "when_to_seek_care": f"If symptoms persist or for individualized clinical evaluation, consult a qualified healthcare professional. [{used_ids[0] if used_ids else 'S1'}]",
            "limitations": "This is general educational information based on authoritative medical sources and is not a medical diagnosis.",
            "used_source_ids": used_ids,
            "uncertainty": "low"
        }

        return LLMGenerationResult(
            raw_output=json.dumps(parsed),
            parsed_json=parsed,
            model_provider="mock",
            model_name="mock-grounded-v1",
            token_usage={"prompt_tokens": 250, "completion_tokens": 120, "total_tokens": 370}
        )


class OpenAICompatibleClient:
    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1", model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def generate_grounded_answer(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 700,
    ) -> LLMGenerationResult:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "response_format": {"type": "json_object"}
        }
        async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT_SECONDS) as client:
            try:
                resp = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
                raw_text = data["choices"][0]["message"]["content"]
                parsed = json.loads(raw_text)
                usage = data.get("usage", {})
                return LLMGenerationResult(
                    raw_output=raw_text,
                    parsed_json=parsed,
                    model_provider="openai_compatible",
                    model_name=self.model,
                    token_usage=usage
                )
            except Exception as e:
                # If API quota is exhausted (429) or network issue, fallback to grounded mock synthesizer
                fallback_client = MockGroundedClient()
                return await fallback_client.generate_grounded_answer(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens
                )


def get_llm_client() -> LLMClient:
    provider = settings.LLM_PROVIDER.lower()
    if provider == "openai_compatible" and settings.LLM_API_KEY:
        return OpenAICompatibleClient(
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL or "https://api.openai.com/v1",
            model=settings.LLM_MODEL
        )
    return MockGroundedClient()


llm_client = get_llm_client()
