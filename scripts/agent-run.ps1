# scripts/agent-run.ps1
param (
    [ValidateSet("Reset-Env", "Run-Tests", "Rebuild-Embeddings", "Full-Build")]
    [string]$Action
)

# Activate Python virtual environment
function Activate-Venv {
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
function Reset-Env {
    Write-Host "Resetting environment..."
    docker-compose down -v
    Remove-Item -Recurse -Force .\chroma, .\qdrant, .\uploads, .\logs -ErrorAction SilentlyContinue
    pip install sentence-transformers
    Write-Host "Environment reset complete."
}

# Run automated test suite
function Run-Tests {
    Write-Host "Running test suite..."
    pytest --maxfail=3 --disable-warnings
    Write-Host "Test execution complete."
}

# Rebuild all document embeddings
function Rebuild-Embeddings {
    Write-Host "Rebuilding vector embeddings from uploaded documents..."
    python .\scripts\embed_all.py
    Write-Host "Embedding process complete."
}

# Perform health check on all container services
function Health-Check {
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
function Full-Build {
    Write-Host "Starting full build sequence (environment reset → Docker build → health check → tests)..."
    Reset-Env
    docker-compose up --build -d
    Health-Check
    Run-Tests
    Write-Host "Full build complete."
}

# Initialize Python environment
Activate-Venv

# Dispatch execution based on selected action
switch ($Action) {
    "Reset-Env"           { Reset-Env; Health-Check }
    "Run-Tests"           { Run-Tests }
    "Rebuild-Embeddings"  { Rebuild-Embeddings }
    "Full-Build"          { Full-Build }
    default               { Write-Host "Unknown action. Please use one of: Reset-Env, Run-Tests, Rebuild-Embeddings, Full-Build." }
}
