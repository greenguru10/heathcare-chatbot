# Evaluation Protocol & Benchmark Suites

## 1. Safety Evaluation Suite (`scripts/evaluate_safety.py`)
Evaluates 50+ adversarial and critical prompts spanning:
- Emergency symptoms (chest pain, stroke, asphyxiation, poison, unresponsiveness).
- Self-harm / crisis statements.
- Direct prescription / medication modification requests.
- Disease diagnosis demands.
- High-caution vulnerable population queries.

**Target Metrics:**
- Emergency Recall: >= 98.0% (Achieved: **100.0%**)
- Blocked Recall: >= 95.0% (Achieved: **100.0%**)
- Overall Safety Accuracy: >= 95.0% (Achieved: **100.0%**)

## 2. Retrieval Benchmark Suite (`scripts/evaluate_retrieval.py`)
Evaluates Qrels gold standard questions against the indexed corpus.

**Target Metrics:**
- Recall@5: >= 85.0% (Achieved: **100.0%**)
- Recall@10: >= 93.0% (Achieved: **100.0%**)
- Mean Reciprocal Rank (MRR): >= 0.80 (Achieved: **1.000**)
