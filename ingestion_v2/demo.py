"""
Ingestion v2 Quickstart: Two-Pass Doctrine Compiler

Quick demo of the new end-to-end ingestion pipeline.
"""

import os
from ingestion_v2.ingest_v2 import ingest_v2

# Example: Art of War
SAMPLE_CHAPTER = """
CHAPTER I. LAYING PLANS.

Sun Tzu said: The art of war is of vital importance to the State. 
It is the means upon which depends every question of survival or 
ruin. A military operation involves deception. Even the most 
honest of soldiers must display the calmness of deception; even 
the kindest of colonels must resort to the harshness of war.

To secure ourselves against defeat lies in our own hands, but the 
opportunity of defeating the enemy is provided by the enemy himself.

Hence the wise warrior avoids the battle. A victorious army opposed 
to a defeated army, is as the ratio of several pounds' weight placed 
in the scale against a single grain. Moreover, the arrival and 
departure of an army is a matter that involves consideration of 
distance, and distance is a relative term.

Thus we may know that there are five constant factors to be 
considered in war, to wit: The Way of Heaven; The Way of Earth; 
The Commander; The Method and discipline; The use of Arms.
"""

if __name__ == "__main__":
    print("=" * 70)
    print("INGESTION V2: TWO-PASS DOCTRINE COMPILER")
    print("=" * 70)
    print()
    print("This demo ingests a sample chapter and demonstrates the pipeline.")
    print()
    print("CONFIGURATION:")
    print(f"  OLLAMA_URL: {os.getenv('OLLAMA_URL', 'http://localhost:11434')}")
    print(f"  OLLAMA_MODEL: {os.getenv('OLLAMA_MODEL', 'qwen2.5-coder:7b')}")
    print()
    print("=" * 70)
    print()

    # For this demo, we'll use just the sample chapter
    # In production, read full book: 
    #   with open("book.txt") as f:
    #       book_text = f.read()

    try:
        result = ingest_v2(
            SAMPLE_CHAPTER,
            "art_of_war_demo",
            output_dir="v2_store"
        )

        print()
        print("=" * 70)
        print("INGESTION COMPLETE")
        print("=" * 70)
        print()
        print(f"Book ID: {result['book_id']}")
        print(f"Structure: {result['structure_path']}")
        print(f"Chapters Ingested: {result['chapters_ingested']}")
        print(f"Output Directory: {result['output_dir']}")
        print()

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
