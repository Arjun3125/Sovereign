import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from cold_strategist.core.interactive import run_interactive_decision
from cold_strategist.core.gatekeeper import Gatekeeper

class M:
    output_shape={'required_fields':['risk_profile.hard_loss_cap_percent']}

answers={'What kind of situation is this? (relationship, career, conflict, money, identity, other)':'business'}

def ask_fn(q):
    print('ASK:', q)
    return answers.get(q, 'never')

ministers={'risk':M(),'finance':M(),'power':M()}
g=Gatekeeper('test'); g.max_questions=0

res=run_interactive_decision('We face potential ruin and bankruptcy; cash flow is collapsing.', ministers, ask_fn, gatekeeper=g)
print('INTERACTIVE RESULT:', res)
