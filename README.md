# Cold Strategist - Sovereign Advisory Council

A sophisticated decision-making system modeled after historical advisory councils, where diverse perspectives (Ministers) deliberate under the guidance of a Sovereign with the counsel of N (Prime Confidant).

## Architecture

### Core Components

- **Sovereign**: The ultimate decision-maker
- **N (Prime Confidant)**: Trusted advisor and liaison
- **Ministers**: Specialized perspectives on different aspects
- **Darbari Council**: Structured deliberation forum
- **Doctrine**: Immutable foundational principles

### Directory Structure

```
cold_strategist/
├── app/                 # Entry points
├── core/                # Non-negotiable core systems
├── darbar/              # Council logic and orchestration
├── ministers/           # All specialized perspectives
├── doctrine/            # Immutable doctrine files
├── context/             # Context building (Layer C)
├── debate/              # Darbari mode deliberation
├── quick/               # Quick mode decision-making
├── memory/              # Immutable event/outcome/pattern stores
├── llm/                 # LLM as a tool (not the system)
├── utils/               # Utilities and guards
└── tests/               # Test suite
```

## Key Principles

1. **Sovereignty**: The Sovereign makes final decisions
2. **Doctrine**: Core principles are immutable and locked
3. **Council**: Multiple perspectives deliberate in structured format
4. **Memory**: All decisions and outcomes are recorded immutably
5. **LLM as Tool**: Language models assist but don't drive decisions

## Ministers

Each minister provides perspective on a specific domain:

- **Grand Strategist**: Long-term vision and strategy
- **Power Analyst**: Power dynamics and influence
- **Psychology Advisor**: Human behavior patterns
- **Diplomacy Expert**: Negotiation and relationships
- **Conflict Resolver**: Conflict analysis and resolution
- **Risk Manager**: Risk assessment and mitigation
- **Timing Expert**: Temporal analysis and timing
- **Tech Advisor**: Technology feasibility
- **Data Analyst**: Evidence and data analysis
- **Adaptation Advisor**: Systems change and adaptation
- **Discipline Enforcer**: Execution quality
- **Legitimacy Guard**: Authority and trust
- **Truth Seeker**: Truth-seeking and reality alignment
- **Option Generator**: Strategic optionality
- **Execution Controller**: Implementation planning

## Usage

### Starting a Session

```python
from app.session_runner import SessionRunner

runner = SessionRunner()
runner.execute()
```

### Conducting Deliberation

```python
from darbar.tribunal import Tribunal

tribunal = Tribunal()
verdict = tribunal.escalate(dispute)
```

## Development

- Tests are located in `/tests`
- Use `unittest` framework for testing
- Follow the immutable doctrine principles
- Respect the sovereignty hierarchy

## Non-Negotiable Principles

- ✓ Doctrine is locked and immutable
- ✓ Memory stores are append-only
- ✓ Sovereign authority is absolute
- ✓ LLM is a tool, not the system
- ✓ All decisions are recorded
