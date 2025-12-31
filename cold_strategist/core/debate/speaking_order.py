"""
Speaking Order - Minister Sequencing (LOCKED)

Determines who speaks first, second, third in each debate phase.

Order rule: Highest score → Lowest score → Middle score

This prevents groupthink:
- Highest conviction doesn't anchor the room
- Lowest conviction airs dissent early
- Middle breaks tie-thinking

No randomness. Deterministic. Same input = same order.
"""

from typing import List, Tuple


class SpeakingOrder:
    """
    Determines the sequence in which ministers present verdicts.
    
    Pattern: High → Low → Middle
    
    Prevents consensus bias by forcing contrasts early.
    """
    
    @staticmethod
    def generate(
        selected_ministers: List[Tuple[str, int]]
    ) -> List[str]:
        """
        Generate speaking order from scored minister list.
        
        Input: [(minister_a, 5), (minister_b, 3), (minister_c, 4)]
        Output: [minister_a, minister_b, minister_c]  (high, low, mid)
        
        Args:
            selected_ministers: List of (minister_name, score) tuples
                              (already sorted by score descending)
        
        Returns:
            List of minister names in speaking order
        """
        if len(selected_ministers) == 0:
            return []
        
        if len(selected_ministers) == 1:
            return [selected_ministers[0][0]]
        
        if len(selected_ministers) == 2:
            # High, then low
            return [selected_ministers[0][0], selected_ministers[1][0]]
        
        # 3+ ministers: High, Low, Middle, rest
        ministers = [m[0] for m in selected_ministers]
        
        order = []
        
        # Highest score speaks first
        order.append(ministers[0])
        
        # Lowest score speaks second (dissent)
        order.append(ministers[-1])
        
        # Middle speaker(s) speak next
        if len(ministers) > 2:
            middle_idx = len(ministers) // 2
            order.append(ministers[middle_idx])
        
        # Rest speak in original score order
        used = {order[0], order[1]}
        if len(order) > 2:
            used.add(order[2])
        
        for minister in ministers:
            if minister not in used:
                order.append(minister)
        
        return order
    
    @staticmethod
    def speaking_order_explanation() -> str:
        """Get explanation of why speaking order matters."""
        return """
SPEAKING ORDER LOGIC (High → Low → Middle):

1. HIGHEST SCORE SPEAKS FIRST
   - Strongest conviction goes on record
   - Does NOT anchor consensus (contradicted by low score next)

2. LOWEST SCORE SPEAKS SECOND
   - Dissent aired immediately
   - Prevents false agreement
   - Forces discussion of doubts early

3. MIDDLE SCORE(S) SPEAK NEXT
   - Tie-breaking perspectives
   - Nuanced positions after stark contrast

This order prevents consensus illusion.
Each position forced to justify itself against explicit counterargument.
"""
