import json
from typing import Dict, Any, List, Optional

from core.llm.ollama_client import OllamaClient
from core.knowledge.synthesize.minister_output_validator import validate_minister_output


SYSTEM_PROMPT = """
You are a Sovereign Minister.

You are NOT an assistant.
You are NOT a narrator.
You are NOT allowed to invent strategy.

Your role:
- Evaluate the user's GOAL strictly using the RETRIEVED DOCTRINES.
- Produce a POSITION, not a plan.
- Use ONLY the retrieved doctrine content.
- Do NOT introduce new facts, tactics, or intentions.

STRICT RULES (NON-NEGOTIABLE):
- Do NOT use emotional or rhetorical language.
- Do NOT persuade.
- Do NOT speculate.
- Do NOT summarize the debate.
- Do NOT reference other ministers.
- Do NOT mention “belief”, “opinion”, or “I think”.

You MUST:
- Choose exactly ONE stance from the allowed set.
- Justify the stance ONLY with doctrine IDs provided.
- List constraints and risks explicitly.
- Return VALID JSON ONLY.
- Follow the schema exactly.

If doctrines are insufficient or irrelevant:
- Set stance to NEEDS_DATA or ABSTAIN.
- Do NOT guess.

Allowed stances:
ADVANCE | DELAY | AVOID | CONDITIONAL | STOP | NEEDS_DATA | ABSTAIN

Your output will be validated strictly.
Invalid output will be discarded.
"""


USER_PROMPT_TEMPLATE = "MINISTER: {minister}\n\nGOAL:\n{goal}\n\nCONTEXT:\n{context}\n\nRETRIEVED DOCTRINES (AUTHORITATIVE):\n{retrieved}\n\nTASK:\nReturn your position as VALID JSON using ONLY the doctrines above."


class MinisterSynthesizer:
    def __init__(self, llm_client: Optional[OllamaClient] = None, model: Optional[str] = None):
        # Accept either an OllamaClient-like object or a simple callable that returns text
        if llm_client is None:
            self.client = OllamaClient()
        elif callable(llm_client) and not hasattr(llm_client, "generate"):
            # Wrap plain callable into an adapter with generate(...) signature
            class _Adapter:
                def __init__(self, func):
                    self.func = func

                def generate(self, *, prompt: str, system: str = None, model: str = None, temperature: float = 0.0, max_tokens: int = 512, stream: bool = False):
                    return self.func(prompt if prompt else "")

            self.client = _Adapter(llm_client)
        else:
            self.client = llm_client
        self.model = model

    def _render_retrieved(self, retrieved: List[Dict[str, Any]]) -> str:
        parts = []
        for r in retrieved:
            did = r.get("doctrine_id") or r.get("id") or r.get("principle_id") or "unknown"
            text = r.get("text") or r.get("excerpt") or r.get("content") or r.get("snippet") or ""
            parts.append(f"DOCTRINE_ID: {did}\nTEXT: {text}\n---")
        return "\n".join(parts)

    def synthesize(
        self,
        minister_name: str,
        goal: str,
        context: Dict[str, Any],
        retrieved: List[Dict[str, Any]],
        confidence_threshold: float = 0.65,
    ) -> Dict[str, Any]:
        """Call LLM with constitutional minister prompts and validate output.

        Returns parsed JSON dict on success, or an empty dict on failure.
        """
        retrieved_text = self._render_retrieved(retrieved)
        ctx_text = json.dumps(context, ensure_ascii=False)

        user_prompt = USER_PROMPT_TEMPLATE.format(
            minister=minister_name,
            goal=goal,
            context=ctx_text,
            retrieved=retrieved_text,
        )

        try:
            resp = self.client.generate(
                prompt=user_prompt,
                system=SYSTEM_PROMPT,
                model=self.model,
                temperature=0.0,
                max_tokens=512,
                stream=False,
            )
        except Exception as e:
            # LLM failure — return empty to let caller handle
            return {}

        # Attempt to parse JSON from response
        try:
            parsed = json.loads(resp)
        except Exception:
            # Try to locate JSON substring
            try:
                start = resp.find("{")
                end = resp.rfind("}")
                if start != -1 and end != -1 and end > start:
                    parsed = json.loads(resp[start:end+1])
                else:
                    return {}
            except Exception:
                return {}

        # Validate structure against retrieved doctrine ids
        retrieved_ids = {r.get("doctrine_id") for r in retrieved if r.get("doctrine_id")}
        try:
            validate_minister_output(parsed, retrieved_doctrine_ids=retrieved_ids)
        except Exception:
            return {}

        return parsed
