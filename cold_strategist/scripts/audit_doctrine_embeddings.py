import sqlite3, json, math, re
from collections import defaultdict

DB_PATH = "../workspace/The_Art_Of_War/embeddings/doctrine_vectors.db"
MAX_TEXT_LEN = 500
DUPLICATE_SIM_THRESHOLD = 0.97
FORBIDDEN_PATTERNS = [r"\bi suggest\b", r"\btherefore\b", r"\bthis implies\b", r"\boptimal strategy\b", r"\brecommend\b", r"\bwe should\b"]
REQUIRED_METADATA_FIELDS = {"doctrine_id","book","chapter","confidence","tags","immutable"}

def cosine_sim(a,b):
    dot = sum(x*y for x,y in zip(a,b))
    na = math.sqrt(sum(x*x for x in a))
    nb = math.sqrt(sum(x*x for x in b))
    return 0.0 if na==0 or nb==0 else dot/(na*nb)

def load_records(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id, text, embedding, metadata FROM embeddings")
    rows = cur.fetchall()
    records = []
    for r in rows:
        records.append({"id": r[0], "text": r[1], "embedding": json.loads(r[2]), "metadata": json.loads(r[3])})
    conn.close()
    return records

def audit(records):
    viol = defaultdict(list)
    for r in records:
        if len(r["text"])>MAX_TEXT_LEN: viol["OVERLONG_TEXT"].append(r["id"])
        if r["text"].count(".")>3: viol["MULTI_CLAIM_TEXT"].append(r["id"])
    for r in records:
        lowered = (r["text"] or "").lower()
        for p in FORBIDDEN_PATTERNS:
            if re.search(p, lowered):
                viol["RUNTIME_LANGUAGE"].append(r["id"]); break
    for r in records:
        m = r["metadata"]
        missing = REQUIRED_METADATA_FIELDS - set(m.keys())
        if missing: viol["MISSING_METADATA"].append((r["id"], sorted(list(missing))))
        if m.get("immutable") is not True: viol["MUTABLE_VECTOR"].append(r["id"])
    n = len(records)
    for i in range(n):
        for j in range(i+1,n):
            sim = cosine_sim(records[i]["embedding"], records[j]["embedding"])
            if sim>=DUPLICATE_SIM_THRESHOLD: viol["DUPLICATE_SEMANTIC"].append((records[i]["id"],records[j]["id"],round(sim,3)))
    return viol

def main():
    print("\\n Doctrine Embedding Audit (PURE PYTHON)\\n")
    try:
        recs = load_records(DB_PATH)
    except Exception as e:
        print(" Failed to open DB:", e); return
    print(f"Loaded {len(recs)} embeddings\\n")
    viol = audit(recs)
    if not viol:
        print(" CLEAN — No violations found\\n SAFE TO CONNECT DARBAR"); return
    print(" VIOLATIONS DETECTED:\\n")
    for k,v in viol.items():
        print(f" {k}: {len(v)}")
        for it in v[:5]: print("   ", it)
        if len(v)>5: print("   ...")
    print("\\n DO NOT CONNECT DARBAR UNTIL FIXED")

if __name__ == '__main__':
    main()
