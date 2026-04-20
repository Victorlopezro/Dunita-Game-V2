# Script para ejecutar el backend localmente durante desarrollo (Windows)

Write-Host "🚀 Iniciando backend de Dunita Game localmente..." -ForegroundColor Green

# Verificar si existe .env
if (!(Test-Path ".env")) {
    Write-Host "⚠️  No se encontró .env, creando uno básico..." -ForegroundColor Yellow
    @"
# Configuración para desarrollo local
REMOTE_API_URL=http://localhost:8000
REMOTE_USER_ID=dev-user
REMOTE_REQUEST_TIMEOUT=8.0
"@ | Out-File -FilePath ".env" -Encoding UTF8
}

# Verificar si existe firebase-service-account.json
if (!(Test-Path "backend/firebase-service-account.json")) {
    Write-Host "⚠️  No se encontró firebase-service-account.json" -ForegroundColor Yellow
    Write-Host "   Para desarrollo local, puedes:" -ForegroundColor Yellow
    Write-Host "   1. Colocar el archivo JSON de credenciales en backend/" -ForegroundColor Yellow
    Write-Host "   2. O usar FIREBASE_CREDENTIALS_JSON en .env" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   Continuando sin Firebase (solo para pruebas)..." -ForegroundColor Yellow
}

# Instalar dependencias si no existe .venv
if (!(Test-Path ".venv")) {
    Write-Host "📦 Creando entorno virtual..." -ForegroundColor Blue
    python -m venv .venv
}

Write-Host "🔧 Activando entorno virtual..." -ForegroundColor Blue
& .\.venv\Scripts\Activate.ps1

Write-Host "📦 Instalando dependencias..." -ForegroundColor Blue
pip install -r backend/requirements.txt

Write-Host "🎮 Iniciando servidor..." -ForegroundColor Green
$env:PYTHONPATH = "$env:PYTHONPATH;$PWD"
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000