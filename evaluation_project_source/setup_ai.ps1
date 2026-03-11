# AI Assistant Installation Script
# Run this after installing Ollama

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AI Assistant Setup for Evaluation App" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check if Ollama is installed
Write-Host "[1/4] Checking Ollama installation..." -ForegroundColor Yellow
try {
    $ollamaVersion = ollama --version
    Write-Host "✓ Ollama is installed: $ollamaVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Ollama is not installed!" -ForegroundColor Red
    Write-Host "Please download and install from: https://ollama.com/download/windows" -ForegroundColor Yellow
    exit 1
}

# Step 2: Check if Python package is installed
Write-Host ""
Write-Host "[2/4] Installing Python packages..." -ForegroundColor Yellow
try {
    pip install ollama --quiet
    Write-Host "✓ ollama package installed" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to install ollama package" -ForegroundColor Red
    exit 1
}

# Step 3: Download AI model
Write-Host ""
Write-Host "[3/4] Checking AI models..." -ForegroundColor Yellow
$modelsList = ollama list

if ($modelsList -like "*llama3.2*") {
    Write-Host "✓ llama3.2 model already downloaded" -ForegroundColor Green
} else {
    Write-Host "Downloading llama3.2 model (this may take a few minutes)..." -ForegroundColor Yellow
    ollama pull llama3.2
    Write-Host "✓ llama3.2 model downloaded" -ForegroundColor Green
}

# Step 4: Test AI
Write-Host ""
Write-Host "[4/4] Testing AI setup..." -ForegroundColor Yellow
try {
    $testResult = python -c "import ollama; ollama.list(); print('OK')"
    if ($testResult -eq "OK") {
        Write-Host "✓ AI is ready to use!" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ Test failed" -ForegroundColor Red
    exit 1
}

# Success message
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  AI Assistant Successfully Installed!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Run: python manage.py runserver" -ForegroundColor White
Write-Host "2. Login to your evaluation system" -ForegroundColor White
Write-Host "3. Look for the purple robot button (bottom-right)" -ForegroundColor White
Write-Host "4. Start chatting with your AI assistant!" -ForegroundColor White
Write-Host ""
Write-Host "For more info, see: AI_ASSISTANT_SETUP_GUIDE.md" -ForegroundColor Yellow
Write-Host ""
