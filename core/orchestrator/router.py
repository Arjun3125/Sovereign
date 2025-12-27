"""
Router - Select Appropriate Engine Based on Mode

Routes CLI calls to quick, normal, or war mode analysis.

Quick Mode is a strategy flag (not a separate engine) that:
- Uses only 3 ministers (Truth, Optionality, Domain-specific)
- Performs 1-shot synthesis with no debate
- Always logs to memory
- Auto-escalates if risk flags trigger

War Mode is a posture filter that:
- Suppresses soft biases (comfort, moral veto, appeasement)
- Enforces hard constraints (legality, no individual targeting)
- Derives leverage and estimates costs
- Decides on safe postures (withdraw, slow_down, apply_pressure)
- Logs all decisions with full audit trail
"""

from typing import Callable, Optional, Any, Dict
from core.orchestrator.war_mode import WarModeEngine, WarContext
from core.orchestrator.war_minister_selector import WarMinisterSelector


# Singleton War Mode Engine (persists across calls)
_war_engine = WarModeEngine()
_war_selector = WarMinisterSelector()


def route(mode: str) -> Callable:
    """
    Route to appropriate engine based on mode.
    
    Args:
        mode: "quick", "normal", or "war"
        
    Returns:
        Engine callable (run method)
    """
    if mode == "quick":
        from core.orchestrator.quick_verdict import QuickEngine
        return QuickEngine().run
    
    elif mode == "war":
        # War Mode: return handler that uses WarModeEngine
        return _handle_war_mode
    
    elif mode == "normal":
        # Knowledge-grounded debate engine (darbar with tribunal)
        from debate.knowledge_debate_engine import KnowledgeGroundedDebateEngine
        from core.knowledge.minister_retriever import MinisterRetriever
        from core.knowledge.synthesize.minister_synthesizer import MinisterSynthesizer
        from darbar.tribunal import Tribunal
        from darbar.n import N
        
        # Initialize components (will be wired with real LLM + index in production)
        # For now, placeholder that will be configured at startup
        def normal_mode_runner(context=None, state=None, **kwargs):
            # TODO: Wire actual retriever, synthesizer, LLM
            engine = KnowledgeGroundedDebateEngine(
                retriever=kwargs.get("retriever"),
                synthesizer=kwargs.get("synthesizer"),
                tribunal=Tribunal(),
                n=N()
            )
            return engine.conduct_debate(
                context=vars(context) if hasattr(context, '__dict__') else context,
                state=vars(state) if hasattr(state, '__dict__') else state,
                goal=getattr(context, 'raw_text', ''),
                confidence_threshold=0.65,
            )
        
        return normal_mode_runner
    
    else:
        raise ValueError(f"Unknown mode: {mode}")


def _handle_war_mode(context=None, state=None, **kwargs) -> Dict[str, Any]:
    """
    War Mode handler: evaluate feasibility, assess constraints, optionally conduct debate.
    
    Flow:
    Phase 1 (Current): Constraint enforcement + posture recommendation
    Phase 2 (Future): If feasible, conduct knowledge-grounded debate with speech filtering
    
    Args:
        context: Context object with goal, domain, reversibility, memory
        state: State object with urgency, emotional_load, etc.
        **kwargs: Additional arguments
            - include_debate: bool (default False) - whether to run debate + apply speech filters
            - retriever: MinisterRetriever (required for debate)
            - synthesizer: MinisterSynthesizer (required for debate)
    
    Returns:
        Dict with assessment, status, recommendation, constraints, costs
        If debate requested: also includes filtered_proceedings + filter_audit
    """
    # Build WarContext from CLI context and state
    war_ctx = WarContext(
        goal=getattr(context, 'raw_text', ''),
        domain=getattr(context, 'domain', 'default'),
        reversibility=getattr(context, 'reversibility', 'unknown'),
        urgency=getattr(state, 'urgency', 0.5),
        emotional_load=getattr(state, 'emotional_load', 0.0),
        prior_context=getattr(context, 'memory', None),
    )
    
    # Evaluate in War Mode
    assessment = _war_engine.evaluate(war_ctx)
    
    # Mandatory logging (even if blocked)
    _war_engine.log(
        assessment,
        notes=f"war_mode from router (domain={war_ctx.domain})"
    )
    
    result = {
        "mode": "war",
        "assessment": assessment,
        "status": assessment.feasibility,
        "recommendation": assessment.recommended_posture,
        "constraints_hit": assessment.constraints_hit,
        "cost_profile": assessment.cost_profile,
        "stop_reason": assessment.stop_reason,
        "leverage_map": assessment.leverage_map,
    }
    
    # Phase 2: Conduct debate with speech filtering (optional)
    if assessment.feasibility != "blocked" and kwargs.get("include_debate", False):
        try:
            from core.orchestrator.war_mode_debate_wrapper import WarModeDebateWrapper
            
            retriever = kwargs.get("retriever")
            synthesizer = kwargs.get("synthesizer")
            
            # Wrap base retriever with War-Aware RAG retriever when in War Mode
            if retriever:
                try:
                    from core.knowledge.war_aware_rag_retriever import WarAwareRAGRetriever
                    from core.knowledge.book_metadata_loader import BookMetadataLoader
                    war_metadata_loader = BookMetadataLoader()
                    war_retriever = WarAwareRAGRetriever(base_retriever=retriever, metadata_loader=war_metadata_loader)
                except Exception:
                    # Fallback to the provided retriever if wrapper unavailable
                    war_retriever = retriever
            else:
                war_retriever = None

            if war_retriever and synthesizer:
                from debate.knowledge_debate_engine import KnowledgeGroundedDebateEngine
                from darbar.tribunal import Tribunal
                from darbar.n import N
                
                # Select War Mode ministers (prefer leverage-heavy voices)
                domain_tags = [war_ctx.domain] if war_ctx.domain else ["default"]
                selected_ministers = _war_selector.select(domain_tags)
                selection_audit = _war_selector.audit(selected_ministers)
                
                # Run debate with War Mode minister selection
                engine = KnowledgeGroundedDebateEngine(
                    retriever=war_retriever,
                    synthesizer=synthesizer,
                    tribunal=Tribunal(),
                    n=N()
                )
                
                proceedings = engine.conduct_debate(
                    context=vars(context) if hasattr(context, '__dict__') else context,
                    state=vars(state) if hasattr(state, '__dict__') else state,
                    goal=war_ctx.goal,
                    selected_ministers=selected_ministers,
                    confidence_threshold=0.65,
                )
                
                # Apply speech filters
                wrapper = WarModeDebateWrapper()
                war_result = wrapper.apply_war_mode_filters(proceedings, mode="war")
                
                result["debate"] = {
                    "original_proceedings": proceedings,
                    "filtered_proceedings": war_result.filtered_proceedings,
                    "filter_audit": war_result.filter_audit,
                    "suppressions_count": war_result.suppressions_count,
                    "filtering_notes": war_result.filtering_notes,
                }
                result["minister_selection"] = selection_audit
        except Exception as e:
            # If debate fails, still return assessment
            result["debate_error"] = str(e)
    
    return result


def route_calibration(mode: str) -> Dict[str, Callable]:
    """
    Route to appropriate calibration/learning module.
    
    Args:
        mode: "quick", "normal", or "war"
        
    Returns:
        Dict with calibrate, posture, and summary callables
    """
    if mode == "quick":
        # Quick Mode uses memory patterns but minimal calibration
        from core.memory.pattern_engine import PatternEngine
        return {
            "calibrate": PatternEngine().detect_patterns,
            "posture": lambda: {"mode": "quick", "description": "1-shot synthesis"},
            "summary": lambda: "Quick Mode: 0 debate, 3 ministers, action-biased."
        }
    
    elif mode == "war":
        # War Mode: export logs and provide summary
        def get_war_logs():
            return _war_engine.export_logs()
        
        def get_war_summary():
            return _war_engine.get_audit_trail()
        
        return {
            "calibrate": get_war_logs,
            "posture": lambda: {"mode": "war", "description": "posture shift + constraint enforcement"},
            "summary": get_war_summary
        }
    
    elif mode == "normal":
        # Standard pattern detection
        from core.memory.pattern_engine import PatternEngine
        return {
            "calibrate": PatternEngine().detect_patterns,
            "posture": lambda: {"description": "baseline"},
            "summary": lambda: "No learning summary available for normal mode."
        }
    
    else:
        raise ValueError(f"Unknown mode: {mode}")


def resolve_mode_with_policy(
    requested_mode: str,
    state: Optional[Any] = None,
    memory_flags: Optional[Dict[str, Any]] = None,
    domain: Optional[str] = None
) -> str:
    """
    Wrap mode_policy.resolve_execution_mode for easy access.
    
    Args:
        requested_mode: User's requested mode
        state: Current state
        memory_flags: Memory-derived signals
        domain: Current domain
        
    Returns:
        Actual mode to use
    """
    from core.orchestrator.mode_policy import resolve_execution_mode
    
    return resolve_execution_mode(
        requested_mode=requested_mode,
        state=state,
        memory_flags=memory_flags,
        domain=domain
    )
