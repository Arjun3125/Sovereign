"""
Activation utilities: Ollama-assisted classifier wrapper and text->minister activation

Provides:
- `classify_text(text, use_ollama=False) -> dict` : returns Ollama-like JSON
- `activate_from_text(text, threshold=0.6, mode=DEFAULT_DARBAR_MODE, use_ollama=False) -> list`

The module falls back to a keyword-based heuristic when Ollama is not available.
"""
from typing import List, Dict, Optional
import shutil
import subprocess
import json
import logging

from cold_strategist.core.selection import minister_registry as registry

LOG = logging.getLogger(__name__)


def _heuristic_classify(text: str) -> Dict:
    """Simple keyword classifier that maps activation keywords to confidences.

    Returns JSON-like dict with key 'activated_domains'.
    """
    text_l = text.lower()
    seen = {}
    for domain, keywords in registry.ACTIVATION_MAP.items():
        for kw in keywords:
            if kw.lower() in text_l:
                # boost exact keyword matches
                seen[domain] = max(seen.get(domain, 0.0), 0.95)
    # fallback weak signals: look for minister keys
    for m in registry.all_ministers():
        if m in text_l and m not in seen:
            seen[m] = max(seen.get(m, 0.0), 0.7)

    activated = []
    for d, c in seen.items():
        activated.append({"domain": d, "confidence": round(float(c), 2)})
    return {"activated_domains": activated}


def classify_text_with_options(text: str, use_ollama: bool = False, ollama_model: Optional[str] = None, timeout: int = 8) -> Dict:
    """
    Classify `text` into activated domains.

    If `use_ollama` is True, attempt to call the `ollama` CLI. If unavailable,
    falls back to the heuristic classifier.

    `timeout` controls the subprocess timeout in seconds.
    """
    if use_ollama:
        ollama_path = shutil.which("ollama")
        LOG.debug("use_ollama requested, ollama_path=%s", ollama_path)
        if ollama_path:
            try:
                prompt = registry.OLLAMA_CLASSIFIER_PROMPT + "\nInput Text:\n" + text
                cmd = [ollama_path, "predict"]
                if ollama_model:
                    cmd += [ollama_model]
                LOG.debug("Calling ollama: %s (timeout=%s)", cmd, timeout)
                proc = subprocess.run(cmd, input=prompt.encode("utf-8"), stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
                out = proc.stdout.decode("utf-8", errors="ignore").strip()
                LOG.debug("ollama stdout: %s", out[:1000])
                # try to find JSON substring
                try:
                    start = out.index("{")
                    end = out.rindex("}") + 1
                    candidate = out[start:end]
                    return json.loads(candidate)
                except Exception:
                    LOG.warning("ollama output not strict JSON, falling back to heuristic")
                    return _heuristic_classify(text)
            except subprocess.TimeoutExpired:
                LOG.warning("ollama call timed out after %ss", timeout)
                return _heuristic_classify(text)
            except Exception as e:
                LOG.exception("ollama call failed: %s", e)
                return _heuristic_classify(text)
        else:
            LOG.debug("ollama binary not found; using heuristic classifier")
            return _heuristic_classify(text)
    else:
        return _heuristic_classify(text)


def classify_text(text: str, use_ollama: bool = False, ollama_model: Optional[str] = None, timeout: int = 8) -> Dict:
    """Compatibility wrapper for simple calls. Keeps same signature but exposes timeout."""
    return classify_text_with_options(text, use_ollama=use_ollama, ollama_model=ollama_model, timeout=timeout)


def activate_from_text(text: str, threshold: float = 0.6, mode: str = registry.DEFAULT_DARBAR_MODE, use_ollama: bool = False, ollama_model: Optional[str] = None, timeout: int = 8) -> List[str]:
    """
    Classify free-text and return the list of active ministers according to
    `registry.active_from_classifier_output` using the given `threshold`.
    """
    classifier_output = classify_text_with_options(text, use_ollama=use_ollama, ollama_model=ollama_model, timeout=timeout)
    return registry.active_from_classifier_output(classifier_output, threshold=threshold, mode=mode)


if __name__ == "__main__":
    # quick manual smoke test
    sample = "We face potential ruin and bankruptcy in 3 months; cash flow is collapsing."
    print(classify_text(sample))
    print(activate_from_text(sample))
