#!/usr/bin/env bash
# Script para ejecutar el backend localmente durante desarrollo

echo "🚀 Iniciando backend de Dunita Game localmente..."

# Verificar si existe .env
if [ ! -f ".env" ]; then
    echo "⚠️  No se encontró .env, creando uno básico..."
    cat > .env << EOF
# Configuración para desarrollo local
REMOTE_API_URL=http://localhost:8000
REMOTE_USER_ID=dev-user
REMOTE_REQUEST_TIMEOUT=8.0
EOF
fi

# Verificar si existe firebase-service-account.json
if [ ! -f "backend/firebase-service-account.json" ]; then
    echo "⚠️  No se encontró firebase-service-account.json"
    echo "   Para desarrollo local, puedes:"
    echo "   1. Colocar el archivo JSON de credenciales en backend/"
    echo "   2. O usar FIREBASE_CREDENTIALS_JSON en .env"
    echo ""
    echo "   Continuando sin Firebase (solo para pruebas)..."
fi

# Instalar dependencias si no existen
if [ ! -d ".venv" ]; then
    echo "📦 Creando entorno virtual..."
    python -m venv .venv
fi

echo "🔧 Activando entorno virtual..."
source .venv/Scripts/activate  # Windows
# source .venv/bin/activate    # Linux/Mac

echo "📦 Instalando dependencias..."
pip install -r backend/requirements.txt

echo "🎮 Iniciando servidor..."
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000