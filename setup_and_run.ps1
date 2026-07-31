Write-Host "Starting DevShield AI X Setup & Run..." -ForegroundColor Cyan

# 1. Setup Backend
Write-Host "`n[1/3] Setting up Backend..." -ForegroundColor Green
Set-Location "backend"

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment and install requirements
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
& .\venv\Scripts\python.exe -m pip install -r requirements.txt

# Handle .env file
if (-not (Test-Path "..\.env")) {
    Write-Host "Creating .env from template..." -ForegroundColor Yellow
    Copy-Item "..\.env.example" "..\.env"
}

# Return to root
Set-Location ".."

# Start Backend in background
Write-Host "Starting FastAPI Backend on port 8000..." -ForegroundColor Green
Start-Process -NoNewWindow -FilePath "backend\venv\Scripts\python.exe" -ArgumentList "-m", "uvicorn", "backend.main:app", "--reload", "--port", "8000", "--host", "127.0.0.1"

# 2. Setup Frontend
Write-Host "`n[2/3] Setting up Frontend..." -ForegroundColor Green
Set-Location "frontend"

if (-not (Test-Path "node_modules")) {
    Write-Host "Installing NPM dependencies..." -ForegroundColor Yellow
    npm install
}

# 3. Start Frontend
Write-Host "`n[3/3] Starting Next.js Frontend on port 3000..." -ForegroundColor Green
npm run dev
