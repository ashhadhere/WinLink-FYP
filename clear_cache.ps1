# Clear Python Cache Script for WinLink
# Run this before starting the worker to ensure latest code is loaded

Write-Host "=" * 60
Write-Host "Clearing Python Cache for WinLink-FYP" -ForegroundColor Cyan
Write-Host "=" * 60
Write-Host ""

$baseDir = "c:\Users\Devsynth-Innovations\Desktop\WinLink-FYP"

# Directories to clear
$cacheDirs = @(
    "$baseDir\__pycache__",
    "$baseDir\worker\__pycache__",
    "$baseDir\core\__pycache__",
    "$baseDir\master\__pycache__",
    "$baseDir\ui\__pycache__",
    "$baseDir\assets\__pycache__"
)

$cleared = 0
$notFound = 0

foreach ($dir in $cacheDirs) {
    if (Test-Path $dir) {
        try {
            Remove-Item -Recurse -Force $dir -ErrorAction Stop
            Write-Host "[OK] Cleared: $dir" -ForegroundColor Green
            $cleared++
        } catch {
            Write-Host "[ERROR] Failed to clear: $dir" -ForegroundColor Red
            Write-Host "        $($_.Exception.Message)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "[SKIP] Not found: $dir" -ForegroundColor Gray
        $notFound++
    }
}

Write-Host ""
Write-Host "=" * 60
Write-Host "Summary:" -ForegroundColor Cyan
Write-Host "  Cleared: $cleared directories" -ForegroundColor Green
Write-Host "  Not found: $notFound directories" -ForegroundColor Gray
Write-Host "=" * 60
Write-Host ""
Write-Host "Python cache cleared successfully!" -ForegroundColor Green
Write-Host "You can now start the worker application with:" -ForegroundColor Yellow
Write-Host "  python launch_enhanced.py" -ForegroundColor White
Write-Host ""
