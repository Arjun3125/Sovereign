# Live ingest progress monitor (PowerShell version)
# Usage: .\utils\monitor_progress.ps1

$metricsFile = "cold_strategist/state/ingest_metrics.json"

while ($true) {
    Clear-Host
    
    if (-not (Test-Path $metricsFile)) {
        Write-Host "📊 Ingest not started yet (metrics file not found)"
        Start-Sleep -Seconds 2
        continue
    }
    
    try {
        $data = Get-Content $metricsFile | ConvertFrom-Json
    }
    catch {
        Write-Host "⚠️  Metrics file corrupted, waiting..."
        Start-Sleep -Seconds 2
        continue
    }
    
    $completed = $data.completed_chunks
    $total = $data.total_chunks
    $percent = $data.percent_complete
    $etaSecs = $data.eta_seconds
    $rate = $data.rate_chunks_per_sec
    
    # Format ETA
    if ($null -eq $etaSecs) {
        $etaStr = "calculating..."
    }
    elseif ($etaSecs -eq 0) {
        $etaStr = "< 1s"
    }
    else {
        $mins = [int]($etaSecs / 60)
        $secs = $etaSecs % 60
        
        if ($mins -gt 0) {
            $etaStr = "$($mins)m $($secs)s"
        }
        else {
            $etaStr = "$($secs)s"
        }
    }
    
    # Display
    Write-Host "=================================================="
    Write-Host "📈 INGEST PROGRESS MONITOR"
    Write-Host "=================================================="
    Write-Host "Progress    : $("{0:000.00}" -f $percent)%"
    Write-Host "Completed   : $('{0:00000}' -f $completed) / $total"
    Write-Host "Rate        : $("{0:0.0}" -f $rate) chunks/sec"
    Write-Host "ETA         : $etaStr"
    Write-Host "=================================================="
    Write-Host "Press Ctrl+C to exit`n"
    
    Start-Sleep -Seconds 2
}
