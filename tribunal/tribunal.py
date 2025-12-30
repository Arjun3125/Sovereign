from .ministers import (
    MinisterOfTruth,
    MinisterOfRisk,
    MinisterOfPower,
    MinisterOfOptionality
)
from .debate import conduct_debate
from .verdict import synthesize_verdict


def convene_tribunal(book_id: str, question: str):
    """Convene the tribunal to debate a question from multiple perspectives.
    
    The tribunal:
    1. Gathers positions from specialized ministers
    2. Synthesizes a structured verdict with agreements/disagreements/risks
    3. Explicitly reserves final authority to human decision maker
    
    Args:
        book_id: Book identifier (must be already ingested).
        question: Question requiring tribunal analysis.
        
    Returns:
        Dict with tribunal_synthesis and minister_positions.
    """
    ministers = [
        MinisterOfTruth(),
        MinisterOfRisk(),
        MinisterOfPower(),
        MinisterOfOptionality()
    ]

    debate = conduct_debate(ministers, book_id, question)
    synthesis = synthesize_verdict(debate, question)

    return {
        "question": question,
        "minister_positions": debate,
        "tribunal_synthesis": synthesis,
        "final_authority": "HUMAN"
    }
