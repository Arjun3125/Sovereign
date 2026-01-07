## 🚀 Quick Start: Production Ingest

### Run Ingest with Progress Monitor

**Terminal 1: Start ingest**
```bash
cd c:\Users\naren\Sovereign
python cold_strategist/scripts/ingest_books.py books --mode full
```

**Terminal 2: Monitor progress**
```bash
cd c:\Users\naren\Sovereign
python utils/monitor_progress.py
```

You'll see:
```
==================================================
📈 INGEST PROGRESS MONITOR
==================================================
Progress    :   25.00%
Completed   :   100 / 2045
Rate        : 5.4 chunks/sec
ETA         : 6m 1s
==================================================
```

### Key Features (All Working ✅)

| Feature | How It Works |
|---------|-------------|
| **Resume-after-crash** | Progress file survives kills. Restart = continue. |
| **Deduplication** | Chunk hashes prevent re-embedding. Auto-skip. |
| **Parallel embedding** | 2 concurrent threads (RTX 4060 safe) |
| **GPU protection** | Semaphore prevents VRAM overload |
| **Live ETA** | Calculated from actual throughput (updated every 2s) |
| **Crash-safe logging** | Append-only ledger survives power loss |
| **Deterministic** | Same input always = same result |

### Files You Need to Know

```
utils/
  ├── hash.py                 ← Chunk fingerprinting
  ├── progress.py             ← Crash-safe ledger
  ├── embedding_guard.py      ← GPU semaphore
  ├── eta.py                  ← ETA computation
  ├── metrics.py              ← Progress file handler
  ├── monitor_progress.py     ← Live monitor
  └── monitor_progress.ps1    ← PowerShell monitor

cold_strategist/
  ├── core/knowledge/ingest/indexer.py     ← Parallel embed + dedup
  └── state/ingest_progress.jsonl          ← Crash-safe ledger
  
core/knowledge/ingest/indexer.py            ← Parallel embed + dedup
cold_strategist/state/ingest_metrics.json   ← Live progress
```

### One-Liner Check (Any Time)

```bash
python -c "import json; from pathlib import Path; from utils.eta import format_eta; d=json.loads(Path('cold_strategist/state/ingest_metrics.json').read_text()); print(f'{d[\"percent_complete\"]}% | {d[\"completed_chunks\"]}/{d[\"total_chunks\"]} | ETA: {format_eta(d.get(\"eta_seconds\"))}')"
```

### Test Resume (Crash Recovery)

1. **Start ingest:**
   ```bash
   python cold_strategist/scripts/ingest_books.py books --mode full
   ```

2. **Wait ~30 seconds, then Ctrl+C** (kill it mid-process)

3. **Restart immediately:**
   ```bash
   python cold_strategist/scripts/ingest_books.py books --mode full
   ```

4. **Check progress:**
   ```bash
   python utils/monitor_progress.py
   ```

You'll see it continues from where it left off (same chunk counts resume).

### Throughput Expected

- **Embedding:** ~1.7-5.7 chunks/sec (depends on Ollama load)
- **ETA:** Auto-calculated (e.g., 100 chunks @ 5/sec = 20 sec remaining)
- **Total ingest:** ~2045 chunks ≈ 6-30 minutes (varies by model)

### Troubleshooting

| Issue | Fix |
|-------|-----|
| Monitor shows "calculating..." | Ingest just started, wait 10 sec |
| ETA seems wrong | It's recalculating from actual rate, wait a bit |
| Metrics file missing | Run `python -c "from utils.metrics import init_metrics; init_metrics(2045)"` |
| GPU semaphore blocking | Expected. Max 2 concurrent embeds intentional. |
| Progress stuck | Check `cold_strategist/state/ingest_progress.jsonl` for errors |

### Canonical Architecture

```
Your Python Code (localhost)
    ↓
Ollama (127.0.0.1:11434)
    ↓
Models:
  - DeepSeek R1 (reasoning)
  - Qwen2.5 (coding)
  - Dolphin (adversarial)
  - Nomic-Embed (vectors)
```

No WebUI in path. No localhost hacks. Pure native Ollama API.

---

**You're all set.** Start ingest + monitor. It'll auto-resume if it crashes.
