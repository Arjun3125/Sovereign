## Progress Monitoring Setup

Your ingest pipeline now has:

✅ **Deterministic ETA computation** from actual throughput  
✅ **Crash-safe metrics file** (`cold_strategist/state/ingest_metrics.json`)  
✅ **Percentage complete** auto-calculated  
✅ **Live refresh monitor** (Python & PowerShell)  

### Quick Start

#### Option 1: Python Monitor (Live, 2-sec refresh)

```bash
python utils/monitor_progress.py
```

Output:
```
==================================================
📈 INGEST PROGRESS MONITOR
==================================================
Progress    :  25.00%
Completed   :    50 / 200
Rate        : 1.7 chunks/sec
ETA         : 1m 30s
==================================================
```

#### Option 2: PowerShell Monitor (Live, 2-sec refresh)

```powershell
.\utils\monitor_progress.ps1
```

Same output as Python version, native PowerShell.

#### Option 3: One-liner Check (No loop)

```bash
python -c "
import json
from pathlib import Path
from utils.eta import format_eta

d = json.loads(Path('cold_strategist/state/ingest_metrics.json').read_text())
print(f\"Progress: {d['percent_complete']}% | ETA: {format_eta(d.get('eta_seconds'))} | {d['completed_chunks']}/{d['total_chunks']}\")
"
```

### Integration with Ingest

To enable metrics in your ingest script:

1. Call `init_metrics(total_chunks)` at start:
   ```python
   from utils.metrics import init_metrics
   init_metrics(total_chunks=2045)  # or whatever your total is
   ```

2. Call `update_metrics(chunks_done)` after each batch:
   ```python
   from utils.metrics import update_metrics
   update_metrics(chunks_just_done=100)
   ```

The metrics file auto-computes:
- `percent_complete` (0-100)
- `eta_seconds` (remaining time estimate)
- `rate_chunks_per_sec` (actual throughput)

### Key Features

🔒 **Crash-Safe**: Progress file survives interrupts  
📊 **Deterministic**: Uses actual elapsed time + completed count  
⚡ **Fast**: Single file read per update  
🎯 **Accurate**: Based on real throughput, not estimates  

### Metrics File Location

```
cold_strategist/state/ingest_metrics.json
```

Example:
```json
{
  "total_chunks": 2045,
  "completed_chunks": 512,
  "start_time": 1735578934.123,
  "last_update": 1735578965.456,
  "percent_complete": 25.03,
  "eta_seconds": 90,
  "rate_chunks_per_sec": 5.7
}
```

### Resume Workflow

Your progress metrics survive crashes:

1. **Ingest starts**: `init_metrics(total_chunks=2045)`
2. **Process 512 chunks**: `update_metrics(512)`
3. **Process crashes**: Kill terminal or Ctrl+C
4. **Restart ingest**: Resume reads progress file, continues from last update
5. **Monitor runs**: Always shows current state

No manual sync needed—the metrics file is your single source of truth.

---

For full integration into ingest scripts, see `utils/metrics.py` and `utils/eta.py`.
