from cold_strategist.core.interactive import run_interactive_decision

class M:
    output_shape = {"required_fields": ["risk_profile.hard_loss_cap_percent"]}

answers = {
    "What kind of situation is this? (relationship, career, conflict, money, identity, other)": "business",
    "What is the worst realistic outcome if nothing changes? (And how bad is that?)": "I could lose 20%",
    "If you choose wrong, can this be undone without lasting damage? (yes/no)": "yes",
    "What emotion is strongest right now? (fear, anger, shame, regret, confusion, something else)": "concerned",
    "Have you faced something structurally similar before? (Describe briefly or 'never')": "never",
}


def ask_fn(q):
    print('ASK:', q)
    return answers.get(q, 'never')


res = run_interactive_decision('A partner violated an agreement', {'risk': M()}, ask_fn)
print('RESULT:', res)
