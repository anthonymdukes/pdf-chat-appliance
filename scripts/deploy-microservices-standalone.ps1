#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Standalone Deploy PDF Chat Appliance Microservices Stack
    
.DESCRIPTION
    Optimized deployment script for IDE terminals with minimal dependencies.
    Designed to avoid stalling issues in integrated terminals.
    
.PARAMETER Action
    Action to perform: deploy, stop, restart, status, logs, cleanup
    
.EXAMPLE
    .\deploy-microservices-standalone.ps1 -Action deploy
    .\deploy-microservices-standalone.ps1 -Action status
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("deploy", "stop", "restart", "status", "logs", "cleanup")]
    [string]$Action
)

# Script configuration
$ScriptName = "deploy-microservices-standalone.ps1"
$StartTime = Get-Date
$ComposeFile = "docker-compose.microservices.yml"

# Disable progress bars and set error handling
$ProgressPreference = "SilentlyContinue"
$ErrorActionPreference = "Continue"

# Simple logging function
function Write-Log {
    param([string]$Message)
    $Timestamp = Get-Date -Format "HH:mm:ss"
    Write-Host "[$Timestamp] $Message"
    # Force immediate output
    if ($Host.UI.RawUI) {
        $Host.UI.RawUI.FlushInputBuffer()
    }
}

# Simple Docker Compose wrapper
function Start-DockerCompose {
    param(
        [string]$Command,
        [int]$TimeoutSeconds = 300
    )
    Write-Log "Running: docker-compose -f $ComposeFile $Command"
    try {
        $ProcessInfo = New-Object System.Diagnostics.ProcessStartInfo
        $ProcessInfo.FileName = "docker-compose"
        $ProcessInfo.Arguments = "-f $ComposeFile $Command"
        $ProcessInfo.UseShellExecute = $false
        $ProcessInfo.RedirectStandardOutput = $true
        $ProcessInfo.RedirectStandardError = $true
        $ProcessInfo.CreateNoWindow = $true
        $Process = New-Object System.Diagnostics.Process
        $Process.StartInfo = $ProcessInfo
        $Process.Start() | Out-Null
        if ($Process.WaitForExit($TimeoutSeconds * 1000)) {
            $Output = $Process.StandardOutput.ReadToEnd()
            $ErrorOutput = $Process.StandardError.ReadToEnd()
            $ExitCode = $Process.ExitCode
            if ($ExitCode -eq 0) {
                Write-Log "Command completed successfully"
                return $Output
            } else {
                Write-Log "Command failed with exit code $ExitCode"
                if ($ErrorOutput) { Write-Log "Error: $ErrorOutput" }
                return $null
            }
        } else {
            Write-Log "Command timed out after $TimeoutSeconds seconds"
            $Process.Kill()
            return $null
        }
    } catch {
        Write-Log "Command execution failed: $($_.Exception.Message)"
        return $null
    } finally {
        if ($Process -and -not $Process.HasExited) {
            $Process.Kill()
        }
    }
}

# Simple health check
function Test-Health {
    param([string]$Url, [string]$Name)
    
    try {
        $Response = Invoke-WebRequest -Uri $Url -TimeoutSec 10 -UseBasicParsing -ErrorAction Stop
        if ($Response.StatusCode -eq 200) {
            Write-Log "PASS: $Name is healthy"
            return $true
        } else {
            Write-Log "WARN: $Name returned status $($Response.StatusCode)"
            return $false
        }
    } catch {
        Write-Log "FAIL: $Name is not responding"
        return $false
    }
}

# Main execution
Write-Log "Starting $ScriptName - Action: $Action"
Write-Log "Working Directory: $(Get-Location)"

# Check if Docker Compose file exists
if (-not (Test-Path $ComposeFile)) {
    Write-Log "ERROR: Docker Compose file not found: $ComposeFile"
    Write-Host ""
    exit 1
}

# Check Docker availability
try {
    docker version | Out-Null
    Write-Log "Docker is available"
} catch {
    Write-Log "ERROR: Docker is not running or not available"
    Write-Host ""
    exit 1
}

# Execute requested action
switch ($Action) {
    "deploy" {
        Write-Log "Deploying microservices stack..."
        Write-Log "Stopping existing containers..."
        Start-DockerCompose -Command "down --remove-orphans" -TimeoutSeconds 60
        Write-Log "Pulling latest images..."
        Start-DockerCompose -Command "pull" -TimeoutSeconds 300
        Write-Log "Starting services..."
        $Result = Start-DockerCompose -Command "up -d --build" -TimeoutSeconds 600
        if ($Result) {
            Write-Log "Services started successfully"
            Write-Log "Waiting for services to start..."
            Start-Sleep -Seconds 30
            Write-Log "Checking service health..."
            $Services = @(
                @{Name="API Gateway"; URL="http://localhost:8000/health"},
                @{Name="LLM Service"; URL="http://localhost:8003/health"},
                @{Name="Vector Store"; URL="http://localhost:8005/health"}
            )
            $HealthyCount = 0
            foreach ($Service in $Services) {
                if (Test-Health -Url $Service.URL -Name $Service.Name) {
                    $HealthyCount++
                }
            }
            Write-Log "Deployment completed. $HealthyCount/$($Services.Count) services healthy"
            Write-Log "Access points:"
            Write-Log "  - API Gateway: http://localhost:8000"
            Write-Log "  - Grafana: http://localhost:3000 (admin/admin)"
            Write-Log "  - Prometheus: http://localhost:9090"
        } else {
            Write-Log "WARNING: Service startup may have encountered issues"
        }
    }
    
    "stop" {
        Write-Log "Stopping microservices stack..."
        Start-DockerCompose -Command "down" -TimeoutSeconds 60
        Write-Log "Services stopped"
    }
    
    "restart" {
        Write-Log "Restarting microservices stack..."
        Start-DockerCompose -Command "restart" -TimeoutSeconds 120
        Write-Log "Services restarted"
    }
    
    "status" {
        Write-Log "Checking service status..."
        $StatusResult = Start-DockerCompose -Command "ps" -TimeoutSeconds 30
        if ($StatusResult) {
            Write-Log "Container status:"
            $StatusResult -split "`n" | ForEach-Object { Write-Log "  $_" }
        }
        
        Write-Log "Service health status:"
        $Services = @(
            @{Name="API Gateway"; URL="http://localhost:8000/health"},
            @{Name="LLM Service"; URL="http://localhost:8003/health"},
            @{Name="Vector Store"; URL="http://localhost:8005/health"}
        )
        
        foreach ($Service in $Services) {
            Test-Health -Url $Service.URL -Name $Service.Name
        }
    }
    
    "logs" {
        Write-Log "Fetching service logs..."
        $LogsResult = Start-DockerCompose -Command "logs --tail=20" -TimeoutSeconds 60
        if ($LogsResult) {
            Write-Log "Recent logs:"
            $LogsResult -split "`n" | ForEach-Object { Write-Log "  $_" }
        }
    }
    
    "cleanup" {
        Write-Log "Performing complete cleanup..."
        
        # Stop and remove containers
        Start-DockerCompose -Command "down --volumes --remove-orphans" -TimeoutSeconds 120
        
        # Remove dangling images
        try {
            docker image prune -f 2>&1 | Out-Null
            Write-Log "Dangling images removed"
        } catch {
            Write-Log "Failed to remove dangling images"
        }
        
        # Remove unused networks
        try {
            docker network prune -f 2>&1 | Out-Null
            Write-Log "Unused networks removed"
        } catch {
            Write-Log "Failed to remove unused networks"
        }
        
        Write-Log "Cleanup completed"
    }
}

# Calculate execution time
$EndTime = Get-Date
$Duration = $EndTime - $StartTime
Write-Log "Script completed in $($Duration.TotalSeconds.ToString('F1')) seconds"

# UNCONDITIONAL: Ensure prompt unsticking
Write-Host "" 