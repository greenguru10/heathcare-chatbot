# Safety Policy & Clinical Governance

## Educational Boundaries
1. **Zero Clinical Diagnosis**: The assistant shall never confirm or diagnose a disease, condition, or medical disorder for a user.
2. **Zero Medication Prescribing**: The assistant shall never recommend specific drug doses, advise changing or stopping prescriptions, or recommend antibiotics.
3. **Emergency Red Flags Preemption**: Any mention of acute chest pain, breathing difficulty, unresponsiveness, acute stroke symptoms, poison ingestion, anaphylaxis, or active seizures immediately triggers the Emergency Protocol without LLM generation or retrieval latency.
4. **Crisis & Self-Harm Support**: Immediate provision of national emergency numbers and crisis helplines (e.g., KIRAN 1800-599-0019 / Tele-MANAS 14416 in India; 988 in the US).
5. **Mandatory Citations & Grounding**: Every factual assertion must be mapped directly to an approved, active, un-superseded source chunk in the form of `[S1]`, `[S2]`.

## Fail-Closed Paradigm
When evidence is incomplete, absent, conflicting, or when safety validators detect unsupported statements, the system returns a safe educational abstention rather than speculative approximations.
