import hashlib


def snapshot_id(universal_principles):
    payload = "".join(sorted(p["id"] for p in universal_principles))
    return hashlib.sha256(payload.encode()).hexdigest()[:12]
