from typing import Dict, Any
from backend.app.safety.rules import SAFETY_CONFIG
from backend.app.core.constants import RiskLevel, ResponseMode


def build_emergency_response(region: str = "IN", is_crisis: bool = False) -> Dict[str, Any]:
    emergency_contacts = SAFETY_CONFIG.get("emergency_contact_by_region", {})
    contact = emergency_contacts.get(region.upper()) or emergency_contacts.get("DEFAULT", {
        "phone": "112 / 911 / 999",
        "service_name": "Emergency Medical Services",
        "crisis_helpline": "National Crisis Hotline"
    })

    if is_crisis:
        answer = (
            "If you are feeling overwhelmed, having thoughts of harming yourself, or in distress, please know that you are not alone and support is available right now.\n\n"
            f"Please reach out immediately to a trained crisis counselor:\n"
            f"- **Emergency Services:** Call **{contact.get('phone', '112')}**\n"
            f"- **Crisis Helpline:** **{contact.get('crisis_helpline', 'Local Mental Health Helpline')}**\n\n"
            "Please talk to someone you trust or reach out to healthcare professionals immediately. I cannot provide crisis intervention or medical diagnosis through chat."
        )
    else:
        answer = (
            "**This may require urgent medical attention.** Please contact your local emergency service now or go to the nearest emergency department immediately.\n\n"
            f"Where available, call **{contact.get('phone', '112')}** for emergency medical assistance.\n"
            "If possible, ask someone nearby to stay with you or help you seek urgent medical care.\n\n"
            "I cannot assess, triage, or treat medical emergencies through chat."
        )

    return {
        "response_mode": ResponseMode.EMERGENCY,
        "risk_level": RiskLevel.RED,
        "answer": answer,
        "key_points": [
            "Emergency situation detected - immediate in-person medical evaluation required.",
            f"Call {contact.get('phone', 'emergency services')} or proceed to the nearest emergency facility.",
            "Do not wait for or rely on automated chat information for urgent health conditions."
        ],
        "when_to_seek_care": "Seek emergency medical care immediately.",
        "limitations": "This system provides educational information only and cannot triage or handle medical emergencies.",
        "confidence": {
            "score": 1.0,
            "label": "high",
            "explanation": "Deterministic safety rule: immediate emergency routing triggered."
        },
        "sources": [],
        "follow_up_suggestions": []
    }


def build_blocked_response(route_name: str) -> Dict[str, Any]:
    if route_name == "blocked_medication_advice":
        answer = (
            "I cannot advise on specific medications, alter doses, or prescribe treatment. "
            "Medication changes must only be made under the supervision of a licensed physician or pharmacist.\n\n"
            "If you are experiencing severe symptoms or adverse drug reactions, contact your prescribing clinician or seek urgent medical care immediately."
        )
    elif route_name == "diagnosis_deferral":
        answer = (
            "I cannot diagnose health conditions or confirm whether you have a specific disease based on symptoms described in chat. "
            "A definitive medical diagnosis requires clinical examination, medical history review, and diagnostic testing by a licensed clinician.\n\n"
            "If you have concerning, severe, or persistent symptoms, please consult a qualified healthcare provider."
        )
    else:
        answer = (
            "I cannot assist with this request as it falls outside the safe educational scope of this healthcare assistant. "
            "Please consult a qualified healthcare professional for personalized clinical advice."
        )

    return {
        "response_mode": ResponseMode.SAFETY_REFUSAL,
        "risk_level": RiskLevel.BLOCKED,
        "answer": answer,
        "key_points": [
            "The assistant is restricted from providing personalized diagnoses or medication prescribing.",
            "Consult a licensed clinician or pharmacist for individual medical guidance."
        ],
        "when_to_seek_care": "Consult a healthcare professional for clinical assessment.",
        "limitations": "Educational information only; does not replace clinician diagnosis or prescription management.",
        "confidence": {
            "score": 1.0,
            "label": "high",
            "explanation": "Deterministic safety boundary enforced."
        },
        "sources": [],
        "follow_up_suggestions": [
            "What questions should I ask my doctor?",
            "What is the approved educational definition of this condition?"
        ]
    }
