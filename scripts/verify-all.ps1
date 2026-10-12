# Verify all subprojects across Python and TypeScript
$ErrorActionPreference = "Stop"
$failed = $false

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "1. Testing debug-warmup (Python)..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Push-Location "debug-warmup"
try {
    python -m pytest tests
    if ($LASTEXITCODE -ne 0) { $failed = $true }
} catch {
    $failed = $true
} finally {
    Pop-Location
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "2. Testing python-ticket-summary (Python)..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Push-Location "python-ticket-summary"
try {
    python -m pytest tests
    if ($LASTEXITCODE -ne 0) { $failed = $true }
} catch {
    $failed = $true
} finally {
    Pop-Location
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "3. Testing typescript-sla-library (Node/Vitest)..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Push-Location "typescript-sla-library"
try {
    npm test
    if ($LASTEXITCODE -ne 0) { $failed = $true }
} catch {
    $failed = $true
} finally {
    Pop-Location
}

Write-Host "`n========================================" -ForegroundColor Cyan
if ($failed) {
    Write-Host "VERIFICATION FAILED: One or more test suites failed." -ForegroundColor Red
    exit 1
} else {
    Write-Host "VERIFICATION SUCCESS: All Python and TypeScript tests passed!" -ForegroundColor Green
    exit 0
}
