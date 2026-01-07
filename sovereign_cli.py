#!/usr/bin/env python
"""Sovereign: Domain-Pure Embedding + Minister Council System"""

import sys
import argparse
from pathlib import Path

# Add sovereign to path
sys.path.insert(0, str(Path(__file__).parent))

from sovereign.embedding.embedding_gatekeeper import run_embedding
from sovereign.retrieval.council_runner import run_council
from sovereign.retrieval.debate_synthesizer import synthesize_debate, extract_disagreements
from sovereign.retrieval.tribunal import tribunal_required, tribunal_verdict

def main():
    ap = argparse.ArgumentParser(description="Sovereign Council System")
    subparsers = ap.add_subparsers(dest="command", help="Commands")
    
    # Embed command
    embed_parser = subparsers.add_parser("embed", help="Embed doctrines from JSON")
    embed_parser.add_argument("--input", default="sovereign/data/doctrine_units.json")
    
    # Query command
    query_parser = subparsers.add_parser("query", help="Run council query")
    query_parser.add_argument("question", help="Question for council", nargs="+")
    query_parser.add_argument("--minister", help="Restrict to one minister")
    
    args = ap.parse_args()
    
    if args.command == "embed":
        print(f"Embedding from {args.input}...")
        run_embedding(args.input)
    
    elif args.command == "query":
        q = " ".join(args.question)
        print(f"Query: {q}\n")
        
        ministers = None
        if args.minister:
            ministers = [args.minister]
        
        council_out = run_council(q, ministers=ministers)
        
        # Show raw council outputs (audit trail)
        print("=" * 60)
        print("RAW COUNCIL OUTPUTS (Audit Trail)")
        print("=" * 60)
        for minister, data in council_out.items():
            print(f"\n[{minister}]")
            print(f"  Confidence: {data['confidence']:.0%}")
            print(f"  Doctrines: {data['count']}")
            if data["doctrines"]:
                for d in data["doctrines"][:2]:
                    print(f"    - {d['doctrine_id']} ({d['score']:.2f})")
        
        # Synthesize debate (Ollama formatter)
        print("\n" + "=" * 60)
        print("COUNCIL DEBATE TRANSCRIPT")
        print("=" * 60)
        debate = synthesize_debate(q, council_out)
        print("\n" + debate)
        
        # Show disagreements
        disagreements = extract_disagreements(council_out)
        if disagreements:
            print("\n" + "=" * 60)
            print("HIGH DISAGREEMENT PAIRS")
            print("=" * 60)
            for m1, m2, spread in disagreements[:3]:
                print(f"  {m1} vs {m2}: {spread:.0%} confidence gap")
        
        # Tribunal verdict
        if tribunal_required(council_out):
            print("\n" + "=" * 60)
            print("TRIBUNAL ACTIVATED (High Disagreement)")
            print("=" * 60)
        
        verdict = tribunal_verdict(council_out)
        print(f"\nFINAL VERDICT: {verdict}")
        print("=" * 60)
    
    else:
        ap.print_help()

if __name__ == "__main__":
    main()
