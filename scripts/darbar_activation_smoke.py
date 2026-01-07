import sys
from pathlib import Path
# Ensure workspace root is on sys.path for local imports
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from cold_strategist.core.darbar import run_full_darbar, SILENCE_STRING
from cold_strategist.core.gatekeeper import Gatekeeper

# Prepare context that meets preconditions
context = {
    'confidence_map': {'overall_context_confidence': 0.8, 'unstable_fields': []}
}
# decision text to activate risk and finance
question = 'We face potential ruin and bankruptcy; cash flow is collapsing within 3 months.'

# Ministers phase1 mapping: include risk and finance positions
ministers_phase1 = {
    'risk': {
        'minister': 'risk',
        'stance': 'OPPOSE',
        'confidence': 0.95,
        'core_claim': 'Downside risk is existential and irreversible',
        'blocking_conditions': [],
        'non_negotiables': ['no_recovery']
    },
    'finance': {
        'minister': 'finance',
        'stance': 'SUPPORT',
        'confidence': 0.9,
        'core_claim': 'We can raise bridge capital to cover runway',
        'blocking_conditions': [],
        'non_negotiables': []
    },
    'power': {
        'minister': 'power',
        'stance': 'ABSTAIN',
        'confidence': 0.5,
        'core_claim': 'Power dynamics not materially changed',
        'blocking_conditions': [],
        'non_negotiables': []
    }
}

# Gatekeeper with budget frozen
g = Gatekeeper('test')
g.max_questions = 0

res = run_full_darbar('did-1', context, ministers_phase1, question, ministers_phase2=None, gatekeeper=g)
print('DARBAR RESULT:', res)
