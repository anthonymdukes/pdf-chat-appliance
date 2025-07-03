# scripts/deployment-validation.ps1
# Autonomous deployment validation cycles for pdf-chat-appliance

param(
    [int]$Cycles = 3,
    [int]$CycleInterval = 30,
    [string]$LogFile = "logs/deployment-validation.log"
)

# Ensure log directory exists
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" -Force | Out-Null
}

function Write-Log {
    param([string]$Message)
    $timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    $logEntry = "[$timestamp] $Message"
    Write-Host $logEntry
    $logEntry | Out-File -Append -Encoding UTF8 $LogFile
}

function Test-ContainerHealth {
    Write-Log "=== Container Health Check ==="
    
    $containers = docker ps --format "{{.Names}},{{.Status}},{{.Health}}" | ConvertFrom-Csv -Header "Name", "Status", "Health"
    
    foreach ($container in $containers) {
        $status = if ($container.Status -like "*Up*") { "SUCCESS Running" } else { "ERROR Not Running" }
        $health = if ($container.Health -like "*healthy*") { "SUCCESS Healthy" } elseif ($container.Health -like "*unhealthy*") { "WARNING Unhealthy" } else { "INFO No Health Check" }
        Write-Log "Container: $($container.Name) - Status: $status - Health: $health"
    }
}

function Test-ServiceEndpoints {
    Write-Log "=== Service Endpoint Validation ==="
    
    $endpoints = @(
        @{Name="Main App"; URL="http://localhost:5000/health"},
        @{Name="Qdrant"; URL="http://localhost:6333/collections"},
        @{Name="Ollama"; URL="http://localhost:11434/api/tags"},
        @{Name="Open WebUI"; URL="http://localhost:8080"}
    )
    
    foreach ($endpoint in $endpoints) {
        try {
            $response = Invoke-WebRequest -Uri $endpoint.URL -UseBasicParsing -TimeoutSec 10
            if ($response.StatusCode -eq 200) {
                Write-Log "SUCCESS $($endpoint.Name): Responding (Status: $($response.StatusCode))"
            } else {
                Write-Log "WARNING $($endpoint.Name): Responding but status $($response.StatusCode)"
            }
        } catch {
            Write-Log "ERROR $($endpoint.Name): Failed to connect - $($_.Exception.Message)"
        }
    }
}

function Test-ModelAvailability {
    Write-Log "=== Model Availability Check ==="
    
    # Check Ollama models
    try {
        $ollamaResponse = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing
        $models = ($ollamaResponse.Content | ConvertFrom-Json).models
        if ($models.Count -eq 0) {
            Write-Log "WARNING Ollama: No models loaded - system may not function properly"
        } else {
            Write-Log "SUCCESS Ollama: $($models.Count) model(s) available"
            foreach ($model in $models) {
                Write-Log "  - $($model.name)"
            }
        }
    } catch {
        Write-Log "ERROR Ollama: Failed to check models - $($_.Exception.Message)"
    }
    
    # Check Qdrant collections
    try {
        $qdrantResponse = Invoke-WebRequest -Uri "http://localhost:6333/collections" -UseBasicParsing
        $collections = ($qdrantResponse.Content | ConvertFrom-Json).result.collections
        Write-Log "SUCCESS Qdrant: $($collections.Count) collection(s) available"
    } catch {
        Write-Log "ERROR Qdrant: Failed to check collections - $($_.Exception.Message)"
    }
}

function Test-ApplicationFunctionality {
    Write-Log "=== Application Functionality Test ==="
    
    # Test main app endpoints
    $appEndpoints = @(
        @{Name="Health"; URL="http://localhost:5000/health"},
        @{Name="Stats"; URL="http://localhost:5000/stats"},
        @{Name="Documents"; URL="http://localhost:5000/documents"}
    )
    
    foreach ($endpoint in $appEndpoints) {
        try {
            $response = Invoke-WebRequest -Uri $endpoint.URL -UseBasicParsing -TimeoutSec 10
            $content = $response.Content | ConvertFrom-Json
            Write-Log "SUCCESS $($endpoint.Name): Functional - $($content.status)"
        } catch {
            Write-Log "ERROR $($endpoint.Name): Failed - $($_.Exception.Message)"
        }
    }
}

function Test-SystemResources {
    Write-Log "=== System Resource Check ==="
    
    # Check disk space
    $disk = Get-WmiObject -Class Win32_LogicalDisk -Filter "DeviceID='C:'"
    $freeSpaceGB = [math]::Round($disk.FreeSpace / 1GB, 2)
    $totalSpaceGB = [math]::Round($disk.Size / 1GB, 2)
    $usagePercent = [math]::Round((($disk.Size - $disk.FreeSpace) / $disk.Size) * 100, 1)
    
    Write-Log "Disk Usage: $freeSpaceGB GB free of $totalSpaceGB GB total ($usagePercent% used)"
    
    if ($freeSpaceGB -lt 5) {
        Write-Log "WARNING Low disk space (< 5GB free)"
    } else {
        Write-Log "SUCCESS Disk space: Adequate"
    }
    
    # Check memory usage
    $memory = Get-WmiObject -Class Win32_OperatingSystem
    $freeMemoryGB = [math]::Round($memory.FreePhysicalMemory / 1MB, 2)
    $totalMemoryGB = [math]::Round($memory.TotalVisibleMemorySize / 1MB, 2)
    $memoryUsagePercent = [math]::Round((($memory.TotalVisibleMemorySize - $memory.FreePhysicalMemory) / $memory.TotalVisibleMemorySize) * 100, 1)
    
    Write-Log "Memory Usage: $freeMemoryGB GB free of $totalMemoryGB GB total ($memoryUsagePercent% used)"
    
    if ($freeMemoryGB -lt 2) {
        Write-Log "WARNING Low memory (< 2GB free)"
    } else {
        Write-Log "SUCCESS Memory: Adequate"
    }
}

function Test-NetworkConnectivity {
    Write-Log "=== Network Connectivity Test ==="
    
    $testUrls = @(
        "https://api.github.com",
        "https://ollama.ai",
        "https://qdrant.io"
    )
    
    foreach ($url in $testUrls) {
        try {
            $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 10
            Write-Log "SUCCESS External connectivity to ${url}: OK"
        } catch {
            Write-Log "WARNING External connectivity to ${url}: Failed - $($_.Exception.Message)"
        }
    }
}

function Run-ValidationCycle {
    param([int]$CycleNumber)
    
    Write-Log "=========================================="
    Write-Log "STARTING VALIDATION CYCLE $CycleNumber of $Cycles"
    Write-Log "=========================================="
    
    Test-ContainerHealth
    Test-ServiceEndpoints
    Test-ModelAvailability
    Test-ApplicationFunctionality
    Test-SystemResources
    Test-NetworkConnectivity
    
    Write-Log "=========================================="
    Write-Log "VALIDATION CYCLE $CycleNumber COMPLETED"
    Write-Log "=========================================="
}

# Main execution
Write-Log "AUTONOMOUS DEPLOYMENT VALIDATION STARTED"
Write-Log "Configuration: $Cycles cycles, $CycleInterval second intervals"
Write-Log "Log file: $LogFile"

for ($i = 1; $i -le $Cycles; $i++) {
    Run-ValidationCycle -CycleNumber $i
    
    if ($i -lt $Cycles) {
        Write-Log "Waiting $CycleInterval seconds before next cycle..."
        Start-Sleep -Seconds $CycleInterval
    }
}

Write-Log "AUTONOMOUS DEPLOYMENT VALIDATION COMPLETED"
Write-Log "Validation results logged to: $LogFile"

# Generate summary
$logContent = Get-Content $LogFile
$errors = ($logContent | Select-String "ERROR").Count
$warnings = ($logContent | Select-String "WARNING").Count
$successes = ($logContent | Select-String "SUCCESS").Count

Write-Log "VALIDATION SUMMARY:"
Write-Log "  Successes: $successes"
Write-Log "  Warnings: $warnings"
Write-Log "  Errors: $errors"

if ($errors -eq 0) {
    Write-Log "DEPLOYMENT VALIDATION: PASSED"
    exit 0
} else {
    Write-Log "DEPLOYMENT VALIDATION: PASSED WITH ISSUES"
    exit 1
} 