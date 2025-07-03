# scripts/agent-run.ps1
param (
    [ValidateSet("Reset-Env", "Run-Tests", "Rebuild-Embeddings", "Full-Build")]
    [string]$Action
)

# 🐍 Activate Python virtual environment
function Activate-Venv {
    $venvPath = ".\.venv\Scripts\Activate.ps1"
    if (Test-Path $venvPath) {
        Write-Host "🐍 Activating Python virtual environment..."
        & $venvPath
        Write-Host "✅ Python venv activated: $env:VIRTUAL_ENV"
    } else {
        Write-Host "❌ Virtual environment not found at $venvPath"
    }
}

# 🧹 Reset services, clean volumes, re-pull dependencies
function Reset-Env {
    Write-Host "🧹 Resetting environment..."
    docker-compose down -v
    Remove-Item -Recurse -Force .\chroma, .\qdrant, .\uploads, .\logs -ErrorAction SilentlyContinue
    pip install sentence-transformers
    Write-Host "✅ Environment reset complete."
}

# 🧪 Run Pytest
function Run-Tests {
    Write-Host "🧪 Running tests..."
    pytest --maxfail=3 --disable-warnings
    Write-Host "✅ Tests executed."
}

# 🧠 Rebuild all vector embeddings
function Rebuild-Embeddings {
    Write-Host "🧠 Rebuilding all embeddings from uploaded documents..."
    python .\scripts\embed_all.py
    Write-Host "✅ Embedding process complete."
}

# 🩺 Health check loop for container services
function Health-Check {
    $healthScript = ".\scripts\health-check.ps1"
    if (Test-Path $healthScript) {
        Write-Host "🩺 Running Docker health check..."
        & $healthScript
    } else {
        Write-Host "⚠️ health-check.ps1 not found. Skipping health check."
    }
}

# 🚀 Complete pipeline: Reset → Docker up → Health → Test
function Full-Build {
    Write-Host "🚀 Starting full build sequence (env reset → Docker build → health check → tests)..."
    Reset-Env
    docker-compose up --build -d
    Health-Check
    Run-Tests
    Write-Host "✅ Full build complete."
}

# ✅ Initialize environment
Activate-Venv

# 🎯 Main logic
switch ($Action) {
    "Reset-Env"           { Reset-Env; Health-Check }
    "Run-Tests"           { Run-Tests }
    "Rebuild-Embeddings"  { Rebuild-Embeddings }
    "Full-Build"          { Full-Build }
    default               { Write-Host "❌ Unknown action. Please use one of: Reset-Env, Run-Tests, Rebuild-Embeddings, Full-Build." }
}
