Write-Host "Starting DevShield AI X 10/10 Architecture..." -ForegroundColor Cyan

# Check for .env file
if (-not (Test-Path ".env")) {
    Write-Host "WARNING: .env file not found. Creating a secure template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
}

# Start the FastAPI Backend in the background
Write-Host "Starting FastAPI Backend Engine on port 8000..." -ForegroundColor Green
$pythonPath = "python"
if (Test-Path "backend\venv\Scripts\python.exe") {
    $pythonPath = "backend\venv\Scripts\python.exe"
}
Start-Process -NoNewWindow -FilePath $pythonPath -ArgumentList "-m", "uvicorn", "backend.main:app", "--reload", "--port", "8000"

# Start the Next.js Frontend
Write-Host "Starting Next.js Frontend on port 3000..." -ForegroundColor Green
Set-Location "frontend"
npm run dev
