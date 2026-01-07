from cold_strategist.core.read_only import ReadOnlyContext


def run_query_mode(mode: str):
    if mode == "FAST_READ_ONLY":
        return ReadOnlyContext()
    return None
