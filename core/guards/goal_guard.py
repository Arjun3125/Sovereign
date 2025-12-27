from typing import List


def detect_goal_misalignment(chunks: List, declared_goal: str) -> bool:
    """
    Mechanical check: returns True if retrieved chunks do NOT mention the declared goal.

    Args:
        chunks: List of KnowledgeChunk (or objects with .text)
        declared_goal: string describing the stated goal

    Returns:
        True if misalignment detected (i.e., none of the chunks seem to advance the goal)
    """
    if not declared_goal:
        return False

    goal_l = declared_goal.lower()
    for c in chunks:
        text = getattr(c, 'text', '') or ''
        if goal_l in text.lower():
            return False

    return True
