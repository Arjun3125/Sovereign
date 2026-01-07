# connect_darbar.py
# CLI-safe Darbar hookup (multi-book federation, read-only, local Ollama)
# Integrated with E (Minister Contracts) and F (Tribunal + Silence)

import os
import json
import argparse
from pathlib import Path
from doctrine_federation import DoctrineFederation
from minister_contracts import gate_minister_output, compute_base_confidence
from tribunal_silence import Tribunal, SilenceManager, PrimeConfidant, TribunalVerdict
from cold_strategist.core.llm.ollama_client import OllamaClient
from cold_strategist.core.knowledge.minister_binding import MINISTER_RAG_BINDING

OLLAMA = OllamaClient()
TRIBUNAL_F = Tribunal()  # Phase F: Tribunal (non-advisory, verdict only)
N_ADVISOR = PrimeConfidant()  # Phase F: N as framer

def discover_doctrine_dbs(root="../workspace"):
    """Discover all doctrine_vectors.db files and map to book names."""
    dbs = {}
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            if f == "doctrine_vectors.db":
                db = os.path.join(dirpath, f)
                book_name = Path(dirpath).parent.name
                dbs[book_name] = db
    return dbs

def run_query(query, minister=None, top_k=6, by_book=False):
    """
    Run Darbar query using federated doctrine retrieval.
    
    Args:
        query: user query string
        minister: restrict to one minister (optional)
        top_k: max results per minister
        by_book: if True, show results grouped by book instead of pooled
    """
    dbs = discover_doctrine_dbs()
    if not dbs:
        print("❌ No doctrine DBs found under cold_strategist/workspace/*/embeddings.")
        return

    fed = DoctrineFederation(dbs)
    print(f"[FEDERATION] Loaded: {len(dbs)} books, ", end="")
    
    # Count total doctrines
    import sqlite3
    total = 0
    for db in dbs.values():
        try:
            count = sqlite3.connect(db).execute("SELECT COUNT(*) FROM embeddings").fetchone()[0]
            total += count
        except:
            pass
    print(f"{total} doctrines\n")

    # Embed query once
    q_vec = OLLAMA.embed(query)

    # Get federated results
    if by_book:
        results_by_book = fed.by_book(q_vec, top_k_per_book=top_k)
        print("\n=== DOCTRINE BY BOOK (NOT POOLED) ===\n")
        for book, hits in results_by_book.items():
            print(f"📖 {book}:")
            for h in hits:
                print(f"  [{h['similarity']:.3f}] {h['doctrine_id'][:40]} — {h['text'][:100]}")
            print()
        return

    # Pooled federation results
    hits = fed.query(q_vec, top_k=top_k * 7)  # get more to distribute

    ministers = [minister] if minister else list(MINISTER_RAG_BINDING.keys())
    minister_outputs = []  # Phase E: collect validated outputs

    for m in ministers:
        binding = MINISTER_RAG_BINDING.get(m, {})
        
        # Get top hits for this minister (no domain filter - semantic matching works)
        m_hits = hits[:top_k]

        # Build minister output (Phase E schema)
        raw_output = {
            "minister": m,
            "position": m_hits[0]["text"] if m_hits else "",
            "citations": [
                {
                    "doctrine_id": h["doctrine_id"],
                    "book": h["book"],
                    "text": h["text"],
                    "similarity": h["similarity"],
                }
                for h in m_hits[:3]
            ],
            "confidence": compute_base_confidence(
                [h["similarity"] for h in m_hits],
                len(m_hits),
            ),
            "risk_flags": [],
        }

        # Gate through E (Minister Contracts) validation
        should_use, gated_output = gate_minister_output(raw_output)
        
        if should_use:
            minister_outputs.append(gated_output)
            print(f"\n--- {m.upper()} ---")
            print(f"Confidence: {gated_output['confidence']:.0%}")
            print(f"Position: {gated_output['position'][:80]}...")
            if gated_output.get("silence_recommended"):
                print("  ⚠️  Silence recommended (low confidence)")
            if gated_output.get("escalation_required"):
                print("  ⚠️  Escalation flagged")
        else:
            print(f"\n--- {m.upper()} --- [GATED OUT]")

    # Phase F: Tribunal judges all outputs
    print("\n\n========== TRIBUNAL JUDGMENT ==========\n")
    
    tribunal_verdict = TRIBUNAL_F.judge(
        minister_outputs=minister_outputs,
        doctrine_sources=[h for h in hits[:10]],
        user_query=query,
    )
    
    print(f"Verdict: {tribunal_verdict['verdict']}")
    print(f"Reason: {tribunal_verdict['reason']}")
    if tribunal_verdict.get("escalation_triggers"):
        print(f"Escalation triggers: {', '.join(tribunal_verdict['escalation_triggers'])}")
    print(f"Confidence: {tribunal_verdict['confidence']:.0%}\n")

    # Phase F: Frame final output via N
    print("\n========== FINAL VERDICT (N) ==========\n")
    
    if tribunal_verdict["verdict"] == "SILENCE":
        silence_text = SilenceManager.frame_silence(
            reason=tribunal_verdict.get("reason", "insufficient_doctrine"),
            confidence=tribunal_verdict["confidence"],
        )
        final_output = N_ADVISOR.frame_verdict(
            tribunal_verdict["verdict"],
            minister_outputs,
            silence_text=silence_text,
            query=query,
        )
    else:
        final_output = N_ADVISOR.frame_verdict(
            tribunal_verdict["verdict"],
            minister_outputs,
            query=query,
        )
    
    print(final_output)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("query", help="Situation / user query text", nargs="+")
    ap.add_argument("--minister", help="Run for a single minister (optional)", default=None)
    ap.add_argument("--top-k", help="Top-K per minister", type=int, default=6)
    ap.add_argument("--by-book", help="Show results grouped by book (not pooled)", action="store_true")
    args = ap.parse_args()
    q = " ".join(args.query)
    run_query(q, minister=args.minister, top_k=args.top_k, by_book=args.by_book)
