def tag_chunk(chunk, meta):
    return {
        **chunk,
        "domains": meta["domains"],
        "allowed_ministers": meta["default_ministers"],
    }
