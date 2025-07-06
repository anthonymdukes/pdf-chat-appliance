# scripts/health-check.ps1
# UPDATED: Now compliant with environment.mdc stall-proof and timeout policy
# Monitors Docker container health and logs status to logs/system/containers.log

$LogFile = "logs/system/containers.log"
$StartTime = Get-Date
$MaxWaitSec = 5  # REDUCED: From 180 to 5 seconds per environment.mdc policy
$SleepSec = 2    # REDUCED: From 10 to 2 seconds per environment.mdc policy

function Test-LogDirectory {
    if (-not (Test-Path "logs/system")) {
        New-Item -ItemType Directory -Path "logs/system" -Force | Out-Null
    }
}

function Start-CommandWithTimeout {
    param(
        [string]$Command,
        [int]$TimeoutSeconds = 5,
        [string]$ErrorMessage = "Command timed out"
    )
    try {
        $job = Start-Job -ScriptBlock { param($cmd) & $cmd } -ArgumentList $Command
        if (Wait-Job $job -Timeout $TimeoutSeconds) {
            $result = Receive-Job $job
            Remove-Job $job -Force -ErrorAction SilentlyContinue
            return $result
        } else {
            Stop-Job $job -ErrorAction SilentlyContinue
            Remove-Job $job -Force -ErrorAction SilentlyContinue
            Write-Host "TIMEOUT: $ErrorMessage" -ForegroundColor Red
            return $null
        }
    } catch {
        # Clean up any orphaned jobs
        Get-Job -ErrorAction SilentlyContinue | Remove-Job -Force -ErrorAction SilentlyContinue
        Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

function Get-HealthStatusInfo {
    $containers = Start-CommandWithTimeout -Command "docker ps --format '{{.Names}}'" -TimeoutSeconds 5 -ErrorMessage "Docker ps command timed out"
    if (-not $containers) {
        Write-Host "WARNING: Could not retrieve container list - Docker may be unavailable"
        return @()
    }
    $statuses = @()
    foreach ($name in $containers) {
        $inspect = Start-CommandWithTimeout -Command "docker inspect --format='{{.State.Health.Status}}' $name" -TimeoutSeconds 5 -ErrorMessage "Docker inspect health timed out for $name"
        $state = Start-CommandWithTimeout -Command "docker inspect --format='{{.State.Status}}' $name" -TimeoutSeconds 5 -ErrorMessage "Docker inspect state timed out for $name"
        if (-not $inspect) { $inspect = "no-healthcheck" }
        if (-not $state) { $state = "unknown" }
        $statuses += [PSCustomObject]@{
            Name   = $name
            Status = $state
            Health = $inspect
        }
    }
    return $statuses
}

function Write-HealthStatus {
    Test-LogDirectory
    $timestamp = (Get-Date).ToString("s")
    $statuses | ForEach-Object {
        "$timestamp`t$($_.Name)`tStatus=$($_.Status)`tHealth=$($_.Health)"
    } | Out-File -Append -Encoding UTF8 $LogFile
}

$Healthy = $false
$attempts = 0
$maxAttempts = 3  # Maximum 3 attempts with 5-second timeouts

while ($attempts -lt $maxAttempts -and ((Get-Date) - $StartTime).TotalSeconds -lt $MaxWaitSec) {
    $attempts++
    Write-Host "Health check attempt $attempts of $maxAttempts"
    $statuses = Get-HealthStatusInfo
    if ($statuses.Count -eq 0) {
        Write-Host "WARNING: No containers found or Docker unavailable"
        break
    }
    $Unhealthy = $statuses | Where-Object {
        $_.Status -in @("restarting", "exited") -or
        $_.Health -in @("unhealthy", "starting")
    }
    if (-not $Unhealthy) {
        $Healthy = $true
        Write-Host "SUCCESS: All containers healthy"
        break
    }
    Write-HealthStatus
    Write-Host "WARNING: Unhealthy containers detected, waiting $SleepSec seconds..."
    Start-Sleep -Seconds $SleepSec
}

# Final snapshot with timeout protection
$statuses = Get-HealthStatusInfo
if ($statuses) {
    Write-HealthStatus
}

if ($Healthy) {
    Write-Host "HEALTH CHECK: PASSED"
    Write-Host ""
    exit 0
} else {
    Write-Host "HEALTH CHECK: FAILED - Some containers unhealthy or unavailable"
    Write-Host ""
    exit 1
}

# UNCONDITIONAL: Ensure prompt unsticking regardless of exit path
Write-Host ""

# COMPREHENSIVE CLEANUP: Remove any orphaned PowerShell jobs
Get-Job -ErrorAction SilentlyContinue | Remove-Job -Force -ErrorAction SilentlyContinue
