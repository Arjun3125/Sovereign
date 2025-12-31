def should_abstain(confidence: float, threshold: float = 0.35) -> bool:
    return confidence < threshold
