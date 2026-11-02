# ============================================================================
# AgriSense - Script de démarrage local sous Windows (Sans Docker)
# Utilise E:\AgriSense_Runtime si le disque C: est plein (44.5 Go libres sur E:)
# ============================================================================

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

# Choisir E:\AgriSense_Runtime si E: existe pour éviter la saturation du disque C:
if (Test-Path "E:\") {
    $RuntimeDir = "E:\AgriSense_Runtime"
} else {
    $RuntimeDir = "$ProjectRoot\.runtime"
}

New-Item -ItemType Directory -Force -Path "$RuntimeDir\temp" | Out-Null
New-Item -ItemType Directory -Force -Path "$RuntimeDir\pip-cache" | Out-Null
New-Item -ItemType Directory -Force -Path "$RuntimeDir\db" | Out-Null

$env:TEMP = "$RuntimeDir\temp"
$env:TMP = "$RuntimeDir\temp"
$env:PIP_CACHE_DIR = "$RuntimeDir\pip-cache"

$VenvDir = "$RuntimeDir\venv"
$PythonExe = "$VenvDir\Scripts\python.exe"
$StreamlitExe = "$VenvDir\Scripts\streamlit.exe"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  AgriSense - Mode Local Léger (Runtime sur $RuntimeDir)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

if (-not (Test-Path $PythonExe)) {
    Write-Host "[1/3] Création de l'environnement virtuel Python dans $VenvDir..." -ForegroundColor Yellow
    python -m venv $VenvDir
}

if (-not (Test-Path $StreamlitExe)) {
    Write-Host "[2/3] Installation des dépendances Python sur $RuntimeDir..." -ForegroundColor Yellow
    & $PythonExe -m pip install --upgrade pip
    & $PythonExe -m pip install fastapi uvicorn pydantic httpx streamlit pandas plotly pytest
} else {
    Write-Host "[2/3] Dépendances Python déjà installées dans $VenvDir." -ForegroundColor Green
}

$DbPath = ($RuntimeDir -replace '\\', '/') + "/db/agrisense_local.db"
$env:DATABASE_URL = "sqlite:///$DbPath"
$env:COLLECTION_SERVICE_URL = "http://127.0.0.1:8001"
$env:PROCESSING_SERVICE_URL = "http://127.0.0.1:8002"
$env:THRESHOLD_TEMPERATURE_MAX = "35.0"
$env:THRESHOLD_SOIL_HUMIDITY_MIN = "25.0"
$env:THRESHOLD_AIR_HUMIDITY_MIN = "30.0"
$env:SIMULATION_INTERVAL_SECONDS = "4"
$env:SIMULATION_ANOMALY_PROBABILITY = "0.25"

Write-Host "[3/3] Démarrage des 4 microservices AgriSense..." -ForegroundColor Green

# Service 1 : Processing Service (Port 8002)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "
    `$Host.UI.RawUI.WindowTitle = 'AgriSense - Processing Service (8002)';
    `$env:TEMP = '$RuntimeDir\temp'; `$env:TMP = '$RuntimeDir\temp';
    `$env:PYTHONPYCACHEPREFIX = '$RuntimeDir\pycache';
    Set-Location '$ProjectRoot\processing-service';
    `$env:DATABASE_URL = '$($env:DATABASE_URL)';
    & '$PythonExe' -m uvicorn app.main:app --host 127.0.0.1 --port 8002
"

Start-Sleep -Seconds 2

# Service 2 : Collection Service (Port 8001)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "
    `$Host.UI.RawUI.WindowTitle = 'AgriSense - Collection Service (8001)';
    `$env:TEMP = '$RuntimeDir\temp'; `$env:TMP = '$RuntimeDir\temp';
    `$env:PYTHONPYCACHEPREFIX = '$RuntimeDir\pycache';
    Set-Location '$ProjectRoot\collection-service';
    `$env:DATABASE_URL = '$($env:DATABASE_URL)';
    `$env:PROCESSING_SERVICE_URL = 'http://127.0.0.1:8002';
    & '$PythonExe' -m uvicorn app.main:app --host 127.0.0.1 --port 8001
"

Start-Sleep -Seconds 2

# Service 3 : Simulateur IoT
Start-Process powershell -ArgumentList "-NoExit", "-Command", "
    `$Host.UI.RawUI.WindowTitle = 'AgriSense - Simulateur IoT';
    `$env:TEMP = '$RuntimeDir\temp'; `$env:TMP = '$RuntimeDir\temp';
    `$env:PYTHONPYCACHEPREFIX = '$RuntimeDir\pycache';
    Set-Location '$ProjectRoot\simulator';
    `$env:COLLECTION_SERVICE_URL = 'http://127.0.0.1:8001';
    `$env:SIMULATION_INTERVAL_SECONDS = '4';
    & '$PythonExe' -u -m app.main
"

# Service 4 : Dashboard Streamlit (Port 8501)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "
    `$Host.UI.RawUI.WindowTitle = 'AgriSense - Dashboard Streamlit (8501)';
    `$env:TEMP = '$RuntimeDir\temp'; `$env:TMP = '$RuntimeDir\temp';
    `$env:PYTHONPYCACHEPREFIX = '$RuntimeDir\pycache';
    Set-Location '$ProjectRoot\dashboard';
    `$env:COLLECTION_SERVICE_URL = 'http://127.0.0.1:8001';
    `$env:PROCESSING_SERVICE_URL = 'http://127.0.0.1:8002';
    & '$StreamlitExe' run app.py --server.port 8501
"

Write-Host ""
Write-Host "Tous les services sont lancés !" -ForegroundColor Green
Write-Host " -> Dashboard Streamlit : http://localhost:8501" -ForegroundColor Cyan
Write-Host " -> API Collecte (Docs) : http://localhost:8001/docs" -ForegroundColor Cyan
Write-Host " -> API Traitement (Docs): http://localhost:8002/docs" -ForegroundColor Cyan
