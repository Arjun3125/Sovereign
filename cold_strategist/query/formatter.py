from cold_strategist.core.llm.ollama_client import OllamaClient

PROMPT = """Rephrase the following strategic principles into a single,
clear, concise answer.

Rules:
- Do NOT add new ideas
- Do NOT infer beyond input
- No moral language
- Do NOT reference authors
- Max 3 sentences

Principles:
{principles}
"""


def phrase_answer(principle_texts):
    """
    principle_texts: list[str]
    """
    joined = "\n".join(f"- {p}" for p in principle_texts)

    # OllamaClient.reason is an instance method; create client and call reason
    client = OllamaClient()
    return client.reason(PROMPT.format(principles=joined))
