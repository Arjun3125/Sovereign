import json, time, os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.eta import format_eta

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def show_progress():
    metrics_file = Path(__file__).parent.parent / "cold_strategist" / "state" / "ingest_metrics.json"
    if not metrics_file.exists():
        print(" Ingest not started yet")
        return
    try:
        data = json.loads(metrics_file.read_text())
    except:
        print("  Metrics corrupted")
        return
    
    completed = data.get("completed_chunks", 0)
    total = data.get("total_chunks", 1)
    percent = data.get("percent_complete", 0.0)
    eta_secs = data.get("eta_seconds")
    rate = data.get("rate_chunks_per_sec", 0.0)
    eta_str = format_eta(eta_secs)
    
    clear_screen()
    print("=" * 50)
    print(" INGEST PROGRESS MONITOR")
    print("=" * 50)
    print(f"Progress    : {percent:6.2f}%")
    print(f"Completed   : {completed:5d} / {total}")
    print(f"Rate        : {rate:.1f} chunks/sec")
    print(f"ETA         : {eta_str}")
    print("=" * 50)
    print("Press Ctrl+C to exit\n")

if __name__ == "__main__":
    try:
        while True:
            show_progress()
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n Monitor stopped")
