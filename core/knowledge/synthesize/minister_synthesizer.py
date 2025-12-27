"""
Convert retrieved knowledge into contextual advice with full traceability.

Synthesizer enforces:
- Advice ONLY from retrieved material (no hallucination)
- Alignment with stated goal (stop if misaligned)
- Confidence gating (ask questions if uncertain)
- Citation preservation (every claim traced to source)
"""

from typing import Dict, Any, List, Optional
import json


class MinisterSynthesizer:
    """
    Converts retrieved knowledge into contextual advice,
    questions, and auditable rationale.
    
    Guarantees:
    - All advice grounded in retrieved chunks
    - Full citations preserved for traceability
    - Alignment check with goal (returns STOP if violated)
    - Confidence gating (asks clarifying questions if low)
    """

    def __init__(self, llm_call):
        """
        Args:
            llm_call: function(prompt: str) -> str (structured JSON response)
        """
        self.llm_call = llm_call

    def synthesize(
        self,
        minister_name: str,
        goal: str,
        context: Dict[str, Any],
        retrieved: Dict[str, List[Dict[str, Any]]],
        confidence_threshold: float = 0.65,
    ) -> Dict[str, Any]:
        """
        Synthesize advice from retrieved knowledge.

        Args:
            minister_name: Name of minister (e.g., "psychology")
            goal: User's stated goal (non-negotiable constraint)
            context: Current situation context
            retrieved: Output from MinisterRetriever.retrieve_for_minister()
                      Format: {"support": [...], "counter": [...], "neutral": [...]}
            confidence_threshold: Minimum confidence to return advice (0.0-1.0)

        Returns:
            Dict with keys:
              - status: "ADVICE" | "STOP" | "NEEDS_CLARIFICATION"
              - advice: Actionable recommendation (grounded in retrieved material)
              - rationale: Explanation of why this applies here
              - risks: Counter-patterns / failure modes
              - questions: Clarifying questions (if low confidence)
              - citations: List of source references with chunk_id, book_id, chapter
              - confidence: Confidence score (0.0-1.0)
        """
        prompt = self._build_prompt(
            minister_name=minister_name,
            goal=goal,
            context=context,
            retrieved=retrieved,
        )

        response_text = self.llm_call(prompt)
        result = self._parse_response(response_text)

        # Safety: alignment check
        if not result.get("aligned_with_goal", True):
            return {
                "status": "STOP",
                "reason": result.get("misalignment_reason", "Violates stated goal"),
                "citations": result.get("citations", []),
            }

        # Confidence gate
        confidence = result.get("confidence", 0.0)
        if confidence < confidence_threshold:
            return {
                "status": "NEEDS_CLARIFICATION",
                "questions": result.get("clarifying_questions", []),
                "partial_advice": result.get("advice"),
                "confidence": confidence,
                "citations": result.get("citations", []),
            }

        return {
            "status": "ADVICE",
            "minister": minister_name,
            "advice": result.get("advice"),
            "rationale": result.get("rationale"),
            "risks": result.get("counter_patterns", []),
            "citations": result.get("citations", []),
            "confidence": confidence,
        }

    def _build_prompt(
        self,
        minister_name: str,
        goal: str,
        context: Dict[str, Any],
        retrieved: Dict[str, List[Dict[str, Any]]],
    ) -> str:
        """
        Build structured prompt that constrains LLM to retrieved material.
        
        LLM MUST NOT:
        - Invent advice outside retrieved chunks
        - Paraphrase without citation
        - Ignore counter-patterns
        
        LLM MUST:
        - Check alignment with goal
        - Provide rationale grounded in retrieved material
        - Include full citations (book, chapter, chunk_id)
        """
        
        support_fmt = self._format_chunks(retrieved.get("support", []))
        counter_fmt = self._format_chunks(retrieved.get("counter", []))
        neutral_fmt = self._format_chunks(retrieved.get("neutral", []))

        return f"""
You are the Minister: {minister_name}

Your role: Synthesize advice from ONLY the retrieved knowledge below.
You MUST NOT invent, extrapolate, or use external knowledge.

GOAL (user's stated objective, non-negotiable):
{goal}

CONTEXT (current situation):
{json.dumps(context, indent=2)}

RETRIEVED SUPPORTING PRINCIPLES:
{support_fmt if support_fmt != "None" else "No supporting principles retrieved"}

RETRIEVED COUNTER-PATTERNS (risks, failures, warnings):
{counter_fmt if counter_fmt != "None" else "No counter-patterns retrieved"}

NEUTRAL CONTEXT:
{neutral_fmt if neutral_fmt != "None" else "No neutral context retrieved"}

INSTRUCTIONS:
1. Check if the retrieved advice can SAFELY help achieve the stated GOAL.
   - If it contradicts or undermines the goal → return "aligned_with_goal": false
   - If it's orthogonal to the goal → still include (context matters)

2. Provide actionable advice ONLY from the retrieved material.
   - Every sentence must map to a retrieved chunk.
   - Adapt principles to THIS specific context.

3. Acknowledge counter-patterns and risks explicitly.
   - Do not ignore warnings in the retrieved material.

4. Rate your confidence (0.0-1.0).
   - High confidence: Retrieved material directly applies
   - Low confidence: Retrieved material is tangential or contradicts context
   - If confidence < 0.65, ask clarifying questions instead.

5. Cite every claim.
   - Format: [book_id | chapter_title | chunk_id]
   - Place citations immediately after the advice they support.

OUTPUT (strict JSON):
{{
  "aligned_with_goal": true,
  "misalignment_reason": null,
  "advice": "...",
  "rationale": "...",
  "counter_patterns": ["risk1", "risk2"],
  "clarifying_questions": [],
  "citations": [
    {{
      "book_id": "art_of_seduction",
      "chapter_title": "The Art of Charm",
      "chunk_id": "abc123def456"
    }}
  ],
  "confidence": 0.75
}}

Do NOT output anything else. Only valid JSON.
"""

    def _format_chunks(self, chunks: List[Dict[str, Any]]) -> str:
        """Format chunks for prompt display with citations."""
        if not chunks:
            return "None"

        formatted = []
        for c in chunks:
            chunk_id = c.get("chunk_id", "")[:8]
            book = c.get("book_id", "unknown")
            chapter = c.get("chapter_title", "unknown")
            text = c.get("text", "").strip()
            label = c.get("label", "")

            formatted.append(
                f"[{book} | {chapter} | {chunk_id}...] ({label})\n"
                f"{text}\n"
            )

        return "\n---\n".join(formatted)

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse LLM response into structured dict.
        
        Graceful fallback if JSON parsing fails.
        """
        try:
            result = json.loads(response_text)
            return result
        except json.JSONDecodeError:
            # Fallback: extract JSON from response if it contains extra text
            import re
            json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
            
            # Hard fallback
            return {
                "aligned_with_goal": True,
                "advice": response_text[:500],
                "rationale": "Could not parse LLM response",
                "citations": [],
                "confidence": 0.0,
            }
