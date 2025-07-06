#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Enterprise Test Script for PDF Chat Appliance Microservices - Phase 2
.DESCRIPTION
    Comprehensive testing of all microservices with end-to-end pipeline validation
    Tests PDF upload, processing, embedding, vector storage, and chat functionality
.PARAMETER Action
    Test action to perform: health, upload, chat, search, full, cleanup
.PARAMETER TestFile
    Path to test PDF file for upload testing
.PARAMETER Query
    Test query for chat and search functionality
#>

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("health", "upload", "chat", "search", "full", "cleanup")]
    [string]$Action = "full",
    
    [Parameter(Mandatory=$false)]
    [string]$TestFile = "uploads/sample-small.pdf",
    
    [Parameter(Mandatory=$false)]
    [string]$Query = "What is the main topic of this document?"
)

# Script configuration
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Service URLs
$API_GATEWAY = "http://localhost:8000"
$PDF_PREPROCESSOR = "http://localhost:8001"
$EMBEDDING_SERVICE = "http://localhost:8002"
$LLM_SERVICE = "http://localhost:8003"
$CHAT_SERVICE = "http://localhost:8004"
$VECTOR_STORE = "http://localhost:8005"

# Test results tracking
$TestResults = @{
    Total = 0
    Passed = 0
    Failed = 0
    Errors = @()
    StartTime = Get-Date
}

function Write-TestResult {
    param(
        [string]$TestName,
        [bool]$Success,
        [string]$Message = "",
        [object]$Data = $null
    )
    
    $TestResults.Total++
    if ($Success) {
        $TestResults.Passed++
        Write-Host "PASS: $TestName" -ForegroundColor Green
        if ($Message) { Write-Host "   $Message" -ForegroundColor Gray }
    } else {
        $TestResults.Failed++
        $TestResults.Errors += "$TestName`: $Message"
        Write-Host "FAIL: $TestName" -ForegroundColor Red
        if ($Message) { Write-Host "   $Message" -ForegroundColor Red }
    }
    
    if ($Data) {
        Write-Host "   Data: $($Data | ConvertTo-Json -Depth 2 -Compress)" -ForegroundColor Cyan
    }
    Write-Host ""
}

function Test-ServiceHealth {
    param([string]$ServiceName, [string]$Url)
    
    try {
        $response = Invoke-RestMethod -Uri "$Url/health" -Method Get -TimeoutSec 10
        $success = $response.status -eq "healthy" -or $response.status -eq "operational"
        Write-TestResult -TestName "$ServiceName Health Check" -Success $success -Message "Status: $($response.status)" -Data $response
        return $success
    } catch {
        Write-TestResult -TestName "$ServiceName Health Check" -Success $false -Message $_.Exception.Message
        return $false
    }
}

function Test-ServiceRoot {
    param([string]$ServiceName, [string]$Url)
    
    try {
        $response = Invoke-RestMethod -Uri $Url -Method Get -TimeoutSec 10
        Write-TestResult -TestName "$ServiceName Root Endpoint" -Success $true -Message "Service operational" -Data $response
        return $true
    } catch {
        Write-TestResult -TestName "$ServiceName Root Endpoint" -Success $false -Message $_.Exception.Message
        return $false
    }
}

function Test-PDFUpload {
    param([string]$FilePath)
    
    try {
        if (-not (Test-Path $FilePath)) {
            Write-TestResult -TestName "PDF Upload" -Success $false -Message "Test file not found: $FilePath"
            return $null
        }
        
        $fileBytes = [System.IO.File]::ReadAllBytes($FilePath)
        $boundary = [System.Guid]::NewGuid().ToString()
        $LF = "`r`n"
        
        $bodyLines = @(
            "--$boundary",
            "Content-Disposition: form-data; name=`"file`"; filename=`"$(Split-Path $FilePath -Leaf)`"",
            "Content-Type: application/pdf",
            "",
            [System.Text.Encoding]::UTF8.GetString($fileBytes),
            "--$boundary--"
        )
        
        $body = $bodyLines -join $LF
        
        $headers = @{
            "Content-Type" = "multipart/form-data; boundary=$boundary"
        }
        
        $response = Invoke-RestMethod -Uri "$PDF_PREPROCESSOR/upload" -Method Post -Body $body -Headers $headers -TimeoutSec 300
        
        Write-TestResult -TestName "PDF Upload" -Success $true -Message "Job ID: $($response.job_id)" -Data $response
        return $response.job_id
    } catch {
        Write-TestResult -TestName "PDF Upload" -Success $false -Message $_.Exception.Message
        return $null
    }
}

function Test-JobStatus {
    param([string]$JobId, [int]$MaxWaitSeconds = 300)
    
    $startTime = Get-Date
    $status = "unknown"
    
    while ((Get-Date) -lt ($startTime.AddSeconds($MaxWaitSeconds))) {
        try {
            $response = Invoke-RestMethod -Uri "$PDF_PREPROCESSOR/job/$JobId" -Method Get -TimeoutSec 10
            $status = $response.status
            $progress = $response.progress
            
            Write-Host "   Job Status: $status (Progress: $progress%)" -ForegroundColor Yellow
            
            if ($status -eq "completed") {
                Write-TestResult -TestName "Job Processing" -Success $true -Message "Job completed successfully" -Data $response
                return $true
            } elseif ($status -eq "failed") {
                Write-TestResult -TestName "Job Processing" -Success $false -Message "Job failed: $($response.error)" -Data $response
                return $false
            }
            
            Start-Sleep -Seconds 10
        } catch {
            Write-Host "   Error checking job status: $($_.Exception.Message)" -ForegroundColor Red
            Start-Sleep -Seconds 5
        }
    }
    
    Write-TestResult -TestName "Job Processing" -Success $false -Message "Job timed out after $MaxWaitSeconds seconds"
    return $false
}

function Test-EmbeddingGeneration {
    try {
        $testTexts = @("This is a test document.", "Another test sentence for embedding.")
        
        $body = @{
            texts = $testTexts
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri "$EMBEDDING_SERVICE/embed" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 30
        
        $success = $response.embeddings.Count -eq $testTexts.Count -and $response.embeddings[0].Count -gt 0
        Write-TestResult -TestName "Embedding Generation" -Success $success -Message "Generated $($response.embeddings.Count) embeddings" -Data $response
        return $success
    } catch {
        Write-TestResult -TestName "Embedding Generation" -Success $false -Message $_.Exception.Message
        return $false
    }
}

function Test-VectorSearch {
    try {
        # First generate a test embedding
        $testTexts = @("test query")
        $body = @{
            texts = $testTexts
        } | ConvertTo-Json
        
        $embeddingResponse = Invoke-RestMethod -Uri "$EMBEDDING_SERVICE/embed" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 30
        
        # Search vector store
        $searchBody = @{
            vector = $embeddingResponse.embeddings[0]
            limit = 5
            score_threshold = 0.5
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri "$VECTOR_STORE/collections/pdf_chunks/search" -Method Post -Body $searchBody -ContentType "application/json" -TimeoutSec 30
        
        Write-TestResult -TestName "Vector Search" -Success $true -Message "Found $($response.results.Count) results" -Data $response
        return $true
    } catch {
        Write-TestResult -TestName "Vector Search" -Success $false -Message $_.Exception.Message
        return $false
    }
}

function Test-ChatFunctionality {
    param([string]$Query)
    
    try {
        $body = @{
            message = $Query
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri "$CHAT_SERVICE/chat" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 60
        
        $success = $response.response -and $response.session_id
        Write-TestResult -TestName "Chat Functionality" -Success $success -Message "Session: $($response.session_id)" -Data $response
        return $response.session_id
    } catch {
        Write-TestResult -TestName "Chat Functionality" -Success $false -Message $_.Exception.Message
        return $null
    }
}

function Test-ContextSearch {
    param([string]$Query)
    
    try {
        $body = @{
            query = $Query
            max_results = 3
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri "$CHAT_SERVICE/search" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 30
        
        Write-TestResult -TestName "Context Search" -Success $true -Message "Found $($response.total_found) results" -Data $response
        return $true
    } catch {
        Write-TestResult -TestName "Context Search" -Success $false -Message $_.Exception.Message
        return $false
    }
}

function Test-LLMGeneration {
    try {
        $body = @{
            prompt = "What is the capital of France?"
            max_tokens = 100
            temperature = 0.7
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri "$LLM_SERVICE/generate" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 60
        
        $success = $response.response -and $response.model
        Write-TestResult -TestName "LLM Generation" -Success $success -Message "Model: $($response.model)" -Data $response
        return $success
    } catch {
        Write-TestResult -TestName "LLM Generation" -Success $false -Message $_.Exception.Message
        return $false
    }
}

function Test-ServiceStats {
    param([string]$ServiceName, [string]$Url)
    
    try {
        $response = Invoke-RestMethod -Uri "$Url/stats" -Method Get -TimeoutSec 10
        Write-TestResult -TestName "$ServiceName Statistics" -Success $true -Message "Stats retrieved" -Data $response
        return $true
    } catch {
        Write-TestResult -TestName "$ServiceName Statistics" -Success $false -Message $_.Exception.Message
        return $false
    }
}

function Test-HealthChecks {
    Write-Host "🏥 Testing Service Health Checks..." -ForegroundColor Cyan
    Write-Host "=" * 50
    
    $services = @(
        @{Name="API Gateway"; Url=$API_GATEWAY},
        @{Name="PDF Preprocessor"; Url=$PDF_PREPROCESSOR},
        @{Name="Embedding Service"; Url=$EMBEDDING_SERVICE},
        @{Name="LLM Service"; Url=$LLM_SERVICE},
        @{Name="Chat Service"; Url=$CHAT_SERVICE},
        @{Name="Vector Store"; Url=$VECTOR_STORE}
    )
    
    $allHealthy = $true
    foreach ($service in $services) {
        $healthy = Test-ServiceHealth -ServiceName $service.Name -Url $service.Url
        if (-not $healthy) { $allHealthy = $false }
    }
    
    return $allHealthy
}

function Test-BasicFunctionality {
    Write-Host "🔧 Testing Basic Service Functionality..." -ForegroundColor Cyan
    Write-Host "=" * 50
    
    $services = @(
        @{Name="API Gateway"; Url=$API_GATEWAY},
        @{Name="PDF Preprocessor"; Url=$PDF_PREPROCESSOR},
        @{Name="Embedding Service"; Url=$EMBEDDING_SERVICE},
        @{Name="LLM Service"; Url=$LLM_SERVICE},
        @{Name="Chat Service"; Url=$CHAT_SERVICE},
        @{Name="Vector Store"; Url=$VECTOR_STORE}
    )
    
    foreach ($service in $services) {
        Test-ServiceRoot -ServiceName $service.Name -Url $service.Url
    }
}

function Test-EmbeddingPipeline {
    Write-Host "Testing Embedding Pipeline..." -ForegroundColor Cyan
    Write-Host "=" * 50
    
    Test-EmbeddingGeneration
    Test-VectorSearch
}

function Test-LLMPipeline {
    Write-Host "🤖 Testing LLM Pipeline..." -ForegroundColor Cyan
    Write-Host "=" * 50
    
    Test-LLMGeneration
}

function Test-ChatPipeline {
    Write-Host "💬 Testing Chat Pipeline..." -ForegroundColor Cyan
    Write-Host "=" * 50
    
    $sessionId = Test-ChatFunctionality -Query $Query
    if ($sessionId) {
        Test-ContextSearch -Query $Query
    }
}

function Test-PDFPipeline {
    Write-Host "📄 Testing PDF Processing Pipeline..." -ForegroundColor Cyan
    Write-Host "=" * 50
    
    $jobId = Test-PDFUpload -FilePath $TestFile
    if ($jobId) {
        Test-JobStatus -JobId $jobId
    }
}

function Test-ServiceStatistics {
    Write-Host "📊 Testing Service Statistics..." -ForegroundColor Cyan
    Write-Host "=" * 50
    
    $services = @(
        @{Name="PDF Preprocessor"; Url=$PDF_PREPROCESSOR},
        @{Name="Embedding Service"; Url=$EMBEDDING_SERVICE},
        @{Name="Chat Service"; Url=$CHAT_SERVICE}
    )
    
    foreach ($service in $services) {
        Test-ServiceStats -ServiceName $service.Name -Url $service.Url
    }
}

function Test-FullPipeline {
    Write-Host "Testing Full End-to-End Pipeline..." -ForegroundColor Cyan
    Write-Host "=" * 50
    
    # Test health first
    $healthy = Test-HealthChecks
    if (-not $healthy) {
        Write-Host "Services are not healthy. Aborting full pipeline test." -ForegroundColor Red
        return
    }
    
    # Test basic functionality
    Test-BasicFunctionality
    
    # Test individual pipelines
    Test-EmbeddingPipeline
    Test-LLMPipeline
    Test-ChatPipeline
    
    # Test PDF processing (if file exists)
    if (Test-Path $TestFile) {
        Test-PDFPipeline
    } else {
        Write-Host "Test file not found: $TestFile" -ForegroundColor Yellow
        Write-Host "   Skipping PDF pipeline test" -ForegroundColor Yellow
    }
    
    # Test statistics
    Test-ServiceStatistics
}

function Show-TestSummary {
    Write-Host ""
    Write-Host "📋 TEST SUMMARY" -ForegroundColor Cyan
    Write-Host "=" * 50
    
    $duration = (Get-Date) - $TestResults.StartTime
    $successRate = if ($TestResults.Total -gt 0) { [math]::Round(($TestResults.Passed / $TestResults.Total) * 100, 1) } else { 0 }
    
    Write-Host "Total Tests: $($TestResults.Total)" -ForegroundColor White
    Write-Host "Passed: $($TestResults.Passed)" -ForegroundColor Green
    Write-Host "Failed: $($TestResults.Failed)" -ForegroundColor Red
    Write-Host "Success Rate: $successRate%" -ForegroundColor $(if ($successRate -ge 80) { "Green" } elseif ($successRate -ge 60) { "Yellow" } else { "Red" })
    Write-Host "Duration: $($duration.ToString('mm\:ss'))" -ForegroundColor White
    
    if ($TestResults.Errors.Count -gt 0) {
        Write-Host ""
        Write-Host "ERRORS:" -ForegroundColor Red
        foreach ($err in $TestResults.Errors) {
            Write-Host "   - $err" -ForegroundColor Red
        }
    }
    
    Write-Host ""
    if ($successRate -ge 80) {
        Write-Host "🎉 Phase 2 Microservices Test PASSED!" -ForegroundColor Green
    } elseif ($successRate -ge 60) {
        Write-Host "Phase 2 Microservices Test PARTIAL - Some issues detected" -ForegroundColor Yellow
    } else {
        Write-Host "Phase 2 Microservices Test FAILED - Major issues detected" -ForegroundColor Red
    }
}

# Main execution
Write-Host "PDF Chat Appliance Microservices - Phase 2 Enterprise Test Suite" -ForegroundColor Cyan
Write-Host "=" * 70
Write-Host "Action: $Action" -ForegroundColor White
Write-Host "Test File: $TestFile" -ForegroundColor White
Write-Host "Query: $Query" -ForegroundColor White
Write-Host "Start Time: $(Get-Date)" -ForegroundColor White
Write-Host ""

try {
    switch ($Action.ToLower()) {
        "health" {
            Test-HealthChecks
        }
        "upload" {
            Test-PDFUpload -FilePath $TestFile
        }
        "chat" {
            Test-ChatFunctionality -Query $Query
        }
        "search" {
            Test-ContextSearch -Query $Query
        }
        "full" {
            Test-FullPipeline
        }
        "cleanup" {
            Write-Host "🧹 Cleanup not implemented in this test script" -ForegroundColor Yellow
        }
        default {
            Write-Host "Unknown action: $Action" -ForegroundColor Red
            exit 1
        }
    }
} catch {
    Write-Host "Test execution failed: $($_.Exception.Message)" -ForegroundColor Red
    $TestResults.Errors += "Test execution failed: $($_.Exception.Message)"
} finally {
    Show-TestSummary
}

# UNCONDITIONAL: Ensure prompt unsticking regardless of exit path
Write-Host ""

# COMPREHENSIVE CLEANUP: Ensure all PowerShell jobs are properly terminated
try {
    Get-Job -ErrorAction SilentlyContinue | Stop-Job -ErrorAction SilentlyContinue
    Get-Job -ErrorAction SilentlyContinue | Remove-Job -ErrorAction SilentlyContinue
} catch {
    # Ignore cleanup errors
}

Write-Host "" 