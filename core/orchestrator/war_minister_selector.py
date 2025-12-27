"""
War Minister Selector

Implements strategic minister selection for War Mode.
Selects which ministers speak based on domain tags and hard rules.

Behavior:
1. Always include Truth (guardrail)
2. Always include Risk & Survival (guardrail)
3. Add preferred ministers matching domain tags
4. Fill remaining slots with conditional ministers
5. Respect max/min minister count
6. Preserve selection order for debate speaking order
"""

from typing import List
from core.orchestrator.war_minister_bias import WAR_MINISTER_BIAS


class WarMinisterSelector:
    """
    Select which ministers participate in War Mode debate.
    
    This reshapes the council without touching doctrines:
    - Ensures leverage-heavy voices dominate
    - Keeps soft voices peripheral (diplomatic/ethical objections deemphasized)
    - Preserves guardrails (Truth, Risk always heard)
    """

    def __init__(self):
        self.bias = WAR_MINISTER_BIAS

    def select(self, domain_tags: List[str]) -> List[str]:
        """
        Select ministers for War Mode debate.
        
        Args:
            domain_tags: List of domain tags (e.g., ["power", "psychology", "timing"])
        
        Returns:
            List of selected minister names in speaking order
        """
        selected = []
        domain_tags_lower = [d.lower() for d in domain_tags]

        # Step 1: Always include guardrails
        if self.bias["hard_rules"]["truth_always_included"]:
            selected.append("Truth")

        if self.bias["hard_rules"]["risk_always_included"]:
            selected.append("Risk & Survival")

        # Step 2: Add preferred ministers matching domain
        for minister in self.bias["preferred"]:
            # Skip if already added (Truth/Risk)
            if minister in selected:
                continue
            
            # Add if relevant to domain
            if self._relevant(minister, domain_tags_lower):
                selected.append(minister)
                
                # Stop if we've hit max ministers
                if len(selected) >= self.bias["hard_rules"]["max_ministers"]:
                    return selected

        # Step 3: Fill remaining slots with conditional ministers
        for minister in self.bias["conditional"]:
            if len(selected) >= self.bias["hard_rules"]["max_ministers"]:
                break
            
            if self._relevant(minister, domain_tags_lower):
                selected.append(minister)

        # Step 4: Ensure minimum council size
        if len(selected) < self.bias["hard_rules"]["min_ministers"]:
            # Fill with next-best preferred ministers (even if not domain-relevant)
            for minister in self.bias["preferred"]:
                if minister not in selected:
                    selected.append(minister)
                    if len(selected) >= self.bias["hard_rules"]["min_ministers"]:
                        break

        # Step 5: Deduplicate and cap
        return list(dict.fromkeys(selected))[:self.bias["hard_rules"]["max_ministers"]]

    def _relevant(self, minister: str, domain_tags_lower: List[str]) -> bool:
        """
        Check if a minister is relevant to the domain tags.
        
        Match logic:
        - Exact match: "Power" in domain_tags
        - Partial match: "power" substring match
        - Alias match: "conflict" → "Conflict"
        """
        minister_lower = minister.lower()
        
        # Exact substring match (e.g., "psychology" in ["power", "psychology", "timing"])
        if minister_lower in domain_tags_lower:
            return True
        
        # Partial match (e.g., "power" matches "power_structures")
        for tag in domain_tags_lower:
            if minister_lower in tag or tag in minister_lower:
                return True
        
        return False

    def audit(self, selected: List[str]) -> dict:
        """
        Return audit info about the selection for transparency.
        
        Returns:
            {
                "selected": [...],
                "count": int,
                "guardrails": ["Truth", "Risk & Survival"],
                "leverage_count": int,
                "soft_count": int,
            }
        """
        guardrails = ["Truth", "Risk & Survival"]
        soft_ministers = {"Diplomacy", "Discipline", "Adaptation"}
        
        leverage = [m for m in selected if m not in guardrails and m not in soft_ministers]
        soft = [m for m in selected if m in soft_ministers]
        
        return {
            "selected": selected,
            "count": len(selected),
            "guardrails": [m for m in guardrails if m in selected],
            "leverage_ministers": leverage,
            "soft_ministers": soft,
            "leverage_count": len(leverage),
            "soft_count": len(soft),
        }
