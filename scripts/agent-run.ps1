# scripts/agent-run.ps1
param (
    [ValidateSet("Reset-Environment", "Invoke-Test", "Update-Embedding", "Invoke-FullBuild")]
    [string]$Action
)

# Activate Python virtual environment
function Enable-VirtualEnvironment {
    $venvPath = ".\.venv\Scripts\Activate.ps1"
    if (Test-Path $venvPath) {
        Write-Host "Activating Python virtual environment..."
        & $venvPath
        Write-Host "Python venv activated: $env:VIRTUAL_ENV"
    } else {
        Write-Host "Virtual environment not found at $venvPath"
    }
}

# Reset services, clean volumes, and re-install dependencies
function Reset-Environment {
    Write-Host "Resetting environment..."
    docker-compose down -v
    Remove-Item -Recurse -Force .\chroma, .\qdrant, .\uploads, .\logs -ErrorAction SilentlyContinue
    pip install sentence-transformers
    Write-Host "Environment reset complete."
}

# Run automated test suite
function Invoke-Test {
    Write-Host "Running test suite..."
    pytest --maxfail=3 --disable-warnings
    Write-Host "Test execution complete."
}

# Rebuild all document embeddings
function Update-Embedding {
    Write-Host "Rebuilding vector embeddings from uploaded documents..."
    python .\scripts\embed_all.py
    Write-Host "Embedding process complete."
}

# Perform health check on all container services
function Test-Health {
    $healthScript = ".\scripts\health-check.ps1"
    if (Test-Path $healthScript) {
        Write-Host "Running Docker health check..."
        & $healthScript
        Write-Host "Health check completed."
    } else {
        Write-Host "health-check.ps1 not found. Skipping health check."
    }
}

# Execute full deployment cycle: Reset → Docker up → Health Check → Tests
function Invoke-FullBuild {
    Write-Host "Starting full build sequence (environment reset → Docker build → health check → tests)..."
    Reset-Environment
    docker-compose up --build -d
    Test-Health
    Invoke-Test
    Write-Host "Full build complete."
}

# Initialize Python environment
Enable-VirtualEnvironment

# Dispatch execution based on selected action
switch ($Action) {
    "Reset-Environment"      { Reset-Environment; Test-Health }
    "Invoke-Test"           { Invoke-Test }
    "Update-Embedding"      { Update-Embedding }
    "Invoke-FullBuild"      { Invoke-FullBuild }
    default                  { Write-Host "Unknown action. Please use one of: Reset-Environment, Invoke-Test, Update-Embedding, Invoke-FullBuild." }
}

Write-Host ""

# UNCONDITIONAL: Ensure prompt unsticking regardless of exit path
Write-Host ""

# COMPREHENSIVE CLEANUP: Remove any orphaned PowerShell jobs and Docker processes
Get-Job -ErrorAction SilentlyContinue | Remove-Job -Force -ErrorAction SilentlyContinue
docker system prune -f --volumes 2>$null | Out-Null
