# Doctrine - The Immutable Foundation

## Core Rules

### 🔒 IMMUTABLE
- Doctrine files are **locked and cannot be modified** at runtime
- Changes to doctrine require explicit Sovereign authorization
- All doctrine changes must be tracked and audited

### 📖 READ-ONLY
- Ministers read doctrine, they do not create it
- Doctrine is loaded once at system initialization
- Doctrine serves as the unchanging reference frame

### 📋 STRUCTURAL
- Doctrine defines principles, not implementations
- Doctrine guides deliberation, it doesn't determine outcomes
- Doctrine is consulted but not automatically obeyed

## File Organization

### Core Authority Files
- `sovereign.yaml` - Sovereign's prerogatives and overrides
- `n.yaml` - Prime Confidant's role and authorities
- `tribunal.yaml` - Escalation and dispute resolution procedures

### Minister Doctrines
Each minister has a locked doctrine file defining their domain:
- `grand_strategist.yaml` - Strategic principles
- `power.yaml` - Power dynamics principles
- `psychology.yaml` - Human behavior principles
- `diplomacy.yaml` - Negotiation principles
- `conflict.yaml` - Conflict resolution principles
- `risk_resources.yaml` - Risk assessment principles
- `timing.yaml` - Temporal analysis principles
- `technology.yaml` - Technology evaluation principles
- `data.yaml` - Evidence and data principles
- `adaptation.yaml` - Systems adaptation principles
- `discipline.yaml` - Execution discipline principles
- `legitimacy.yaml` - Authority and legitimacy principles
- `truth.yaml` - Truth-seeking principles
- `optionality.yaml` - Strategic optionality principles
- `executor.yaml` - Execution control principles

## Loading and Access

Doctrine is loaded at system startup via `doctrine_loader.py`:

```python
loader = DoctrineLoader()
all_doctrines = loader.load_all_doctrines()
minister_doctrine = loader.load_doctrine("grand_strategist")
```

## Governance

- Doctrine is the **primary source of truth** for minister behavior
- Changing doctrine requires Sovereign decree
- All doctrine changes are logged and tracked
- Historical versions are maintained for audit trails

## Security

- Doctrine files are read-only at runtime (file permissions enforced)
- Doctrine integrity is verified on every load
- Tampering with doctrine triggers system alerts
- Backups are maintained automatically
