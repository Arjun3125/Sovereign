"""
Output Rendering - Format and Display Results

Renders verdicts, patterns, and calibrations in human-readable format.
"""


def render_verdict(verdict: dict):
    """
    Render a verdict (normal or war mode) to stdout.
    
    Args:
        verdict: Verdict dict from WarEngine or standard engine
    """
    print("\n" + "="*70)
    print("VERDICT")
    print("="*70)
    
    # Main verdict
    verdict_text = verdict.get("VERDICT", "UNKNOWN")
    print(f"\n{verdict_text}")
    
    # Primary move / recommendation
    if "PRIMARY_MOVE" in verdict:
        print(f"\nPrimary Move:\n  {verdict['PRIMARY_MOVE']}")
    elif "verdict" in verdict:
        print(f"\nRecommendation:\n  {verdict['verdict']}")
    
    # Posture
    posture = verdict.get("VERDICT", verdict.get("posture", "unknown"))
    print(f"\nPosture: {posture}")
    
    # Risk (war mode)
    if "RISK" in verdict:
        risk = float(verdict.get("RISK", 0.5))
        risk_visual = "▓" * int(risk * 10) + "░" * (10 - int(risk * 10))
        print(f"\nRisk: {risk_visual} {risk:.1%}")
    
    # Reversibility (war mode)
    if "REVERSIBLE" in verdict:
        reversible = verdict.get("REVERSIBLE")
        print(f"Reversible: {'Yes' if reversible else 'No'}")
    
    # Optionality (war mode)
    if "OPTIONALITY" in verdict:
        print(f"Optionality: {verdict['OPTIONALITY']}")
    
    # Alternatives
    if "ALTERNATIVES" in verdict and verdict["ALTERNATIVES"]:
        print(f"\nAlternatives:")
        for i, alt in enumerate(verdict["ALTERNATIVES"], 1):
            print(f"  {i}. {alt}")
    
    # DO NOT constraints
    if "DO_NOT" in verdict and verdict["DO_NOT"]:
        print(f"\nDO NOT:")
        for constraint in verdict["DO_NOT"]:
            print(f"  ✗ {constraint}")
    
    # Next step
    if "NEXT" in verdict:
        print(f"\nNext Step:\n  {verdict['NEXT']}")
    
    # Illusions detected
    if "illusions_detected" in verdict and verdict["illusions_detected"]:
        print(f"\nIllusions Detected:")
        for illusion in verdict["illusions_detected"]:
            print(f"  ⚠ {illusion}")
    
    # Event ID (for later outcome resolution)
    if "EVENT_ID" in verdict:
        print(f"\n" + "-"*70)
        print(f"Event ID (save for outcome resolution): {verdict['EVENT_ID']}")
        print("-"*70)
    
    print()


def render_patterns(patterns: list):
    """
    Render detected patterns.
    
    Args:
        patterns: List of Pattern objects
    """
    if not patterns:
        print("\nNo recurring patterns detected.\n")
        return
    
    print("\n" + "="*70)
    print("DETECTED PATTERNS")
    print("="*70 + "\n")
    
    for pattern in patterns:
        print(f"• {pattern.pattern_name}")
        print(f"  Type: {pattern.pattern_type}")
        print(f"  Frequency: {pattern.frequency}")
        if pattern.domain:
            print(f"  Domain: {pattern.domain}")
        if pattern.last_outcome:
            print(f"  Last Outcome: {pattern.last_outcome}")
        print()


def render_calibration(posture: dict):
    """
    Render N's calibration/posture adjustments.
    
    Args:
        posture: Posture dict from get_n_war_posture or similar
    """
    print("\n" + "="*70)
    print("N'S ADJUSTED POSTURE")
    print("="*70 + "\n")
    
    if "description" in posture:
        print(f"Posture: {posture['description']}\n")
    
    if "caution" in posture:
        caution = float(posture["caution"])
        caution_visual = "⬆" if caution < 1.0 else "⬇" if caution > 1.0 else "→"
        print(f"Caution: {caution_visual} {caution:.2f}x")
    
    if "urgency_threshold" in posture:
        urgency = float(posture["urgency_threshold"])
        urgency_visual = "⬆" if urgency > 1.0 else "⬇" if urgency < 1.0 else "→"
        print(f"Urgency Threshold: {urgency_visual} {urgency:.2f}x")
    
    if "bluntness" in posture:
        bluntness = float(posture["bluntness"])
        bluntness_visual = "⬆" if bluntness > 1.0 else "⬇" if bluntness < 1.0 else "→"
        print(f"Bluntness: {bluntness_visual} {bluntness:.2f}x")
    
    print()


def render_learning_summary(summary_text: str):
    """
    Render learning summary.
    
    Args:
        summary_text: Summary text from summarize_war_learning or similar
    """
    print("\n" + "="*70)
    print("LEARNING SUMMARY")
    print("="*70 + "\n")
    print(summary_text)
    print()


def render_error(error_msg: str):
    """
    Render error message.
    
    Args:
        error_msg: Error message
    """
    print("\n" + "="*70)
    print("ERROR")
    print("="*70)
    print(f"\n{error_msg}\n")
