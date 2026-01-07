# Starting Ollama for Ingestion

The ingestion model requires Ollama to be running for LLM calls.

## Quick Start

1. **Start Ollama service:**
   ```powershell
   # If Ollama is installed, just run:
   ollama serve
   ```

2. **Or start it in the background:**
   ```powershell
   Start-Process ollama -ArgumentList "serve"
   ```

3. **Verify it's running:**
   ```powershell
   # Check if port 11434 is listening
   Test-NetConnection -ComputerName localhost -Port 11434
   ```

4. **Then run ingestion:**
   ```powershell
   python ingest_art_of_war.py
   ```

## Alternative: Use Existing Structure

If you have a previous structure file, the ingestion will resume from Phase-2.

## Check Ollama Status

```powershell
# Check if Ollama process is running
Get-Process -Name ollama -ErrorAction SilentlyContinue

# Check if the API is accessible
curl http://127.0.0.1:11434/api/tags
```

