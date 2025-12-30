from query_engine.ask import ask


class Minister:
    """Base class for advisory ministers.
    
    Each minister specializes in a particular lens on the doctrine.
    """
    name = "BaseMinister"

    def advise(self, book_id: str, question: str) -> str:
        """Provide advice on a question using this minister's specialty.
        
        Args:
            book_id: Book identifier.
            question: Question to answer.
            
        Returns:
            Minister's advice as string.
        """
        raise NotImplementedError


class MinisterOfTruth(Minister):
    """Ensures factual consistency with doctrine."""
    name = "Minister of Truth"

    def advise(self, book_id, question):
        return ask(book_id, f"[FACTUAL CONSISTENCY ONLY]\n{question}")


class MinisterOfRisk(Minister):
    """Identifies risks, failure modes, and unintended consequences."""
    name = "Minister of Risk"

    def advise(self, book_id, question):
        return ask(book_id, f"[RISKS / FAILURE MODES]\n{question}")


class MinisterOfPower(Minister):
    """Analyzes power dynamics, leverage, and optics."""
    name = "Minister of Power"

    def advise(self, book_id, question):
        return ask(book_id, f"[POWER / LEVERAGE / OPTICS]\n{question}")


class MinisterOfOptionality(Minister):
    """Explores alternatives, escape routes, and optionality."""
    name = "Minister of Optionality"

    def advise(self, book_id, question):
        return ask(book_id, f"[ALTERNATIVES / ESCAPE OPTIONS]\n{question}")
