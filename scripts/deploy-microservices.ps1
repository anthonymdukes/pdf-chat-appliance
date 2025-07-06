#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Deploy PDF Chat Appliance Microservices Stack
    
.DESCRIPTION
    Deploys the complete microservices architecture with monitoring,
    health checks, and enterprise-scale optimizations.
    
.PARAMETER Action
    Action to perform: deploy, stop, restart, status, logs, cleanup
    
.PARAMETER Environment
    Environment to deploy: dev, staging, prod (default: dev)
    
.EXAMPLE
    .\deploy-microservices.ps1 -Action deploy -Environment dev
    .\deploy-microservices.ps1 -Action status
    .\deploy-microservices.ps1 -Action cleanup
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("deploy", "stop", "restart", "status", "logs", "cleanup")]
    [string]$Action,
    
    [Parameter(Mandatory=$false)]
    [ValidateSet("dev", "staging", "prod")]
    [string]$Environment = "dev"
)

# Script configuration
$ScriptName = "deploy-microservices.ps1"
$StartTime = Get-Date
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Logging function
function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$Timestamp] [$Level] $Message"
    [System.Console]::Out.Flush()
}

# Error handling function
function Stop-Deployment {
    param(
        [string]$ErrorMessage,
        [int]$ExitCode = 1
    )
    Write-Log "ERROR: $ErrorMessage" "ERROR"
    Write-Log "Script execution failed. Exit code: $ExitCode" "ERROR"
    [System.Console]::Out.Flush()
    exit $ExitCode
}

# Safe Docker Compose execution with timeout
function Start-DockerCompose {
    param(
        [string]$Command,
        [string]$ComposeFile,
        [int]$TimeoutSeconds = 300
    )
    try {
        Write-Log "Executing: docker-compose -f $ComposeFile $Command"
        $Job = Start-Job -ScriptBlock {
            param($ComposeFile, $Command)
            Set-Location $using:PWD
            & docker-compose -f $ComposeFile $Command 2>&1
        } -ArgumentList $ComposeFile, $Command
        $Result = Wait-Job -Job $Job -Timeout $TimeoutSeconds
        if ($Result) {
            $Output = Receive-Job -Job $Job
            Remove-Job -Job $Job -Force
            return $Output
        } else {
            Write-Log "Docker Compose command timed out after $TimeoutSeconds seconds" "WARN"
            Stop-Job -Job $Job -Force
            Remove-Job -Job $Job -Force
            return $null
        }
    } catch {
        Write-Log "Docker Compose execution failed: $($_.Exception.Message)" "ERROR"
        return $null
    }
}

# Safe web request with timeout
function Test-WebRequest {
    param(
        [string]$Url,
        [int]$TimeoutSeconds = 10
    )
    try {
        $Response = Invoke-WebRequest -Uri $Url -TimeoutSec $TimeoutSeconds -UseBasicParsing
        return $Response
    } catch {
        Write-Log "Web request failed for $Url : $($_.Exception.Message)" "WARN"
        return $null
    }
}

# Cleanup function
function Clear-Resource {
    Write-Log "Cleaning up resources..."
    try {
        Get-Job -State Running -ErrorAction SilentlyContinue | 
            Stop-Job -PassThru -ErrorAction SilentlyContinue | 
            Remove-Job -Force -ErrorAction SilentlyContinue
        Get-Process -Name "docker*" -ErrorAction SilentlyContinue | 
            Stop-Process -Force -ErrorAction SilentlyContinue
        [System.GC]::Collect()
        [System.GC]::WaitForPendingFinalizers()
        Write-Log "Cleanup completed"
    } catch {
        Write-Log "Cleanup encountered errors: $($_.Exception.Message)" "WARN"
    }
}

# Register cleanup on script exit
trap {
    Write-Log "Script interrupted. Performing cleanup..." "WARN"
    Clear-Resource
    Write-Host ""
    [System.Console]::Out.Flush()
    break
}

# Main execution
try {
    Write-Log "Starting $ScriptName - Action: $Action, Environment: $Environment"
    Write-Log "Working Directory: $(Get-Location)"
    Write-Log "Checking Docker availability..."
    try {
        docker version 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Docker is available"
        } else {
            Stop-Deployment "Docker is not running or not available. Please start Docker Desktop."
        }
    }
    catch {
        Stop-Deployment "Docker is not running or not available. Please start Docker Desktop."
    }
    $ComposeFile = "docker-compose.microservices.yml"
    if (-not (Test-Path $ComposeFile)) {
        Stop-Deployment "Docker Compose file not found: $ComposeFile"
    }
    switch ($Action) {
        "deploy" {
            Write-Log "Deploying microservices stack..."
            Write-Log "Stopping existing containers..."
            $StopResult = Start-DockerCompose -Command "down --remove-orphans" -ComposeFile $ComposeFile -TimeoutSeconds 60
            if ($StopResult) {
                Write-Log "Existing containers stopped"
            }
            Write-Log "Pulling latest images..."
            $PullResult = Start-DockerCompose -Command "pull" -ComposeFile $ComposeFile -TimeoutSeconds 300
            if ($PullResult) {
                Write-Log "Images pulled successfully"
            }
            Write-Log "Building and starting services..."
            $UpResult = Start-DockerCompose -Command "up -d --build" -ComposeFile $ComposeFile -TimeoutSeconds 600
            if ($UpResult) {
                Write-Log "Services started successfully"
            } else {
                Write-Log "Service startup may have encountered issues" "WARN"
            }
            
            # Wait for services to be healthy
            Write-Log "Waiting for services to be healthy..."
            Start-Sleep -Seconds 30
            
            # Check service health with timeouts
            Write-Log "Checking service health..."
            $HealthChecks = @(
                @{Name="API Gateway"; URL="http://localhost:8000/health"},
                @{Name="LLM Service"; URL="http://localhost:8003/health"},
                @{Name="Vector Store"; URL="http://localhost:8005/health"},
                @{Name="Prometheus"; URL="http://localhost:9090/-/healthy"},
                @{Name="Grafana"; URL="http://localhost:3000/api/health"}
            )
            
            $HealthyCount = 0
            foreach ($HealthCheck in $HealthChecks) {
                try {
                    $Response = Test-WebRequest -Url $HealthCheck.URL -TimeoutSeconds 15
                    if ($Response -and $Response.StatusCode -eq 200) {
                        Write-Log "PASS: $($HealthCheck.Name) is healthy"
                        $HealthyCount++
                    } else {
                        Write-Log "WARN: $($HealthCheck.Name) returned status $($Response.StatusCode)" "WARN"
                    }
                }
                catch {
                    Write-Log "FAIL: $($HealthCheck.Name) is not responding" "WARN"
                }
            }
            
            Write-Log "Deployment completed. $HealthyCount/$($HealthChecks.Count) services healthy"
            Write-Log "Access points:"
            Write-Log "  - API Gateway: http://localhost:8000"
            Write-Log "  - Grafana: http://localhost:3000 (admin/admin)"
            Write-Log "  - Prometheus: http://localhost:9090"
        }
        
        "stop" {
            Write-Log "Stopping microservices stack..."
            $StopResult = Start-DockerCompose -Command "down" -ComposeFile $ComposeFile -TimeoutSeconds 60
            if ($StopResult) {
                Write-Log "Services stopped"
            }
        }
        
        "restart" {
            Write-Log "Restarting microservices stack..."
            $RestartResult = Start-DockerCompose -Command "restart" -ComposeFile $ComposeFile -TimeoutSeconds 120
            if ($RestartResult) {
                Write-Log "Services restarted"
            }
        }
        
        "status" {
            Write-Log "Checking service status..."
            $StatusResult = Start-DockerCompose -Command "ps" -ComposeFile $ComposeFile -TimeoutSeconds 30
            if ($StatusResult) {
                Write-Log "Container status:"
                $StatusResult | ForEach-Object { Write-Log "  $_" }
            }
            
            Write-Log "Service health status:"
            $Services = @(
                @{Name="API Gateway"; URL="http://localhost:8000/health"},
                @{Name="LLM Service"; URL="http://localhost:8003/health"},
                @{Name="Vector Store"; URL="http://localhost:8005/health"},
                @{Name="Prometheus"; URL="http://localhost:9090/-/healthy"},
                @{Name="Grafana"; URL="http://localhost:3000/api/health"}
            )
            
            foreach ($Service in $Services) {
                try {
                    $Response = Test-WebRequest -Url $Service.URL -TimeoutSeconds 10
                    if ($Response -and $Response.StatusCode -eq 200) {
                        Write-Log "PASS: $($Service.Name): Healthy"
                    } else {
                        Write-Log "FAIL: $($Service.Name): Unhealthy"
                    }
                }
                catch {
                    Write-Log "FAIL: $($Service.Name): Unhealthy"
                }
            }
        }
        
        "logs" {
            Write-Log "Fetching service logs..."
            $LogsResult = Start-DockerCompose -Command "logs --tail=50" -ComposeFile $ComposeFile -TimeoutSeconds 60
            if ($LogsResult) {
                $LogsResult | ForEach-Object { Write-Log "  $_" }
            }
        }
        
        "cleanup" {
            Write-Log "Performing complete cleanup..."
            
            # Stop and remove containers
            $DownResult = Start-DockerCompose -Command "down --volumes --remove-orphans" -ComposeFile $ComposeFile -TimeoutSeconds 120
            if ($DownResult) {
                Write-Log "Containers and volumes removed"
            }
            
            # Remove dangling images
            try {
                docker image prune -f 2>&1 | Out-Null
                Write-Log "Dangling images removed"
            } catch {
                Write-Log "Failed to remove dangling images" "WARN"
            }
            
            # Remove unused networks
            try {
                docker network prune -f 2>&1 | Out-Null
                Write-Log "Unused networks removed"
            } catch {
                Write-Log "Failed to remove unused networks" "WARN"
            }
            
            # Clean up local resources
            Clear-Resource
            
            Write-Log "Cleanup completed"
        }
    }
    
    # Calculate execution time
    $EndTime = Get-Date
    $Duration = $EndTime - $StartTime
    Write-Log "Script completed successfully in $($Duration.TotalSeconds.ToString('F2')) seconds"
}

catch {
    Stop-Deployment "Unexpected error: $($_.Exception.Message)"
}

finally {
    # Final cleanup
    Clear-Resource
    
    # UNCONDITIONAL: Ensure prompt unsticking regardless of exit path
    Write-Host ""
    [System.Console]::Out.Flush()
}

# UNCONDITIONAL: Ensure prompt unsticking regardless of exit path
Write-Host ""
[System.Console]::Out.Flush() 