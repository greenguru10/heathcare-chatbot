from typing import List, Dict, Any


class EvidenceSelector:
    def __init__(self, final_k: int = 4, max_per_doc: int = 2):
        self.final_k = final_k
        self.max_per_doc = max_per_doc

    def select(self, ranked_candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        selected: List[Dict[str, Any]] = []
        doc_counts: Dict[str, int] = {}

        for item in ranked_candidates:
            if len(selected) >= self.final_k:
                break

            chunk = item["chunk"]
            doc_id = chunk["document_id"]
            current_count = doc_counts.get(doc_id, 0)

            if current_count < self.max_per_doc:
                item["selected_as_evidence"] = True
                selected.append(item)
                doc_counts[doc_id] = current_count + 1

        return selected


evidence_selector = EvidenceSelector()
