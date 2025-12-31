import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from debate.knowledge_debate_engine import KnowledgeGroundedDebateEngine
from core.knowledge.synthesize.minister_synthesizer import MinisterSynthesizer
from core.knowledge.minister_retriever import MinisterRetriever
from darbar.tribunal import Tribunal
from darbar.n import N

# instantiate minimal components

# Minimal dummy vector index and embed function for smoke
class _DummyIndex:
	def search(self, emb, k=10):
		# return dummy chunks compatible with MinisterRetriever expectations
		return [
			{
				"chunk_id": "48L_1",
				"book_id": "48_Laws_of_Power",
				"chapter_title": "Law 1",
				"text": "Always say less than necessary.",
				"label": "principle",
				"domains": ["negotiation"],
			},
			{
				"chunk_id": "AoS_3",
				"book_id": "Art_of_Seduction",
				"chapter_title": "Charm",
				"text": "Frame interactions with subtlety.",
				"label": "example",
				"domains": ["negotiation"],
			}
		]

def _dummy_embed(q):
	return [0.0]

retriever = MinisterRetriever(rag_index=_DummyIndex(), embed_fn=_dummy_embed)
def _dummy_llm(prompt: str) -> str:
	# Return a simple structured JSON response expected by MinisterSynthesizer
	return '''{
		"aligned_with_goal": true,
		"advice": "Apply calibrated pressure within diplomatic channels.",
		"rationale": "Grounded in principle: scarcity and leverage.",
		"counter_patterns": ["reputational_risk"],
		"clarifying_questions": [],
		"citations": [{"book_id": "48_Laws_of_Power", "chapter_title": "Law 1", "chunk_id": "48L_1"}],
		"confidence": 0.8
	}'''

synth = MinisterSynthesizer(_dummy_llm)
engine = KnowledgeGroundedDebateEngine(retriever=retriever, synthesizer=synth, tribunal=Tribunal(), n=N())

context = {"raw_text":"Test debate about influence and power","domain":"negotiation","summary":"Test summary"}
state = {"mode":"war","emotional_load":0.2,"stakes":"high","urgency":0.8}

proc = engine.conduct_debate(context=context, state=state, goal="Get better deal", include_audit=True)
print('Debate completed. Positions:', [p.minister for p in proc.positions])
