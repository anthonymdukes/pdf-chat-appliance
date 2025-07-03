# scripts/health-check.ps1
# Monitors Docker container health and logs status to logs/system/containers.log

$LogFile = "logs/system/containers.log"
$StartTime = Get-Date
$MaxWaitSec = 180
$SleepSec = 10
$Failures = @()

function Ensure-LogDir {
    if (-not (Test-Path "logs/system")) {
        New-Item -ItemType Directory -Path "logs/system" -Force | Out-Null
    }
}

function Get-HealthStatus {
    docker ps --format "{{.Names}}" | ForEach-Object {
        $name = $_
        $inspect = docker inspect --format="{{.State.Health.Status}}" $name 2>$null
        $state = docker inspect --format="{{.State.Status}}" $name 2>$null

        if ($inspect -eq "") { $inspect = "no-healthcheck" }
        if ($state -eq "") { $state = "unknown" }

        [PSCustomObject]@{
            Name   = $name
            Status = $state
            Health = $inspect
        }
    }
}

function Log-Status {
    Ensure-LogDir
    $timestamp = (Get-Date).ToString("s")
    $statuses | ForEach-Object {
        "$timestamp`t$($_.Name)`tStatus=$($_.Status)`tHealth=$($_.Health)"
    } | Out-File -Append -Encoding UTF8 $LogFile
}

$Healthy = $false

while (((Get-Date) - $StartTime).TotalSeconds -lt $MaxWaitSec) {
    $statuses = Get-HealthStatus

    $Unhealthy = $statuses | Where-Object {
        $_.Status -in @("restarting", "exited") -or
        $_.Health -in @("unhealthy", "starting")
    }

    if (-not $Unhealthy) {
        $Healthy = $true
        break
    }

    Log-Status
    Start-Sleep -Seconds $SleepSec
}

# Final snapshot
$statuses = Get-HealthStatus
Log-Status

if ($Healthy) {
    exit 0
} else {
    exit 1
}
