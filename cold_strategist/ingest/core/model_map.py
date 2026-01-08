"""Model assignment for Ingest V2 roles.

Defines which LLM or embedding model to use for each ingestion role.
This file is authoritative for the pipeline's model choices.

Note: during PHASE 0 (dry run) the deterministic local extractors
in this folder may be used instead of live LLM calls. See README
or the ingest activation sequence for details.
"""

MODEL_ASSIGNMENTS = {
    # Domain classification: fast, stable classifier
    "domain_classification": "llama3.1:8b",

    # Memory extraction for INGEST uses the clerk model LLaMA 3.1
    "memory_extraction": "llama3.1:8b",

    # Embeddings used for indexing after ingestion
    "embeddings": "nomic-embed-text:latest",

    # Runtime reasoning models are out-of-band for ingest and unchanged
}


def get_model_for(role: str) -> str:
    """Return the assigned model for a given role.

    Raises KeyError for unknown roles.
    """
    return MODEL_ASSIGNMENTS[role]
