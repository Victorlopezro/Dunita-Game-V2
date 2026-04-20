#!/usr/bin/env python3
"""
Script de prueba para el backend de Dunita Game
Ejecuta pruebas básicas contra el backend desplegado
"""

import requests
import json
import sys
import os
from pathlib import Path

def test_backend(base_url: str):
    """Prueba los endpoints básicos del backend"""

    print(f"🔍 Probando backend en: {base_url}")
    print("=" * 50)

    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check: {data}")
        else:
            print(f"❌ Health check falló: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error en health check: {e}")
        return False

    # Test 2: Game data
    try:
        response = requests.get(f"{base_url}/game-data")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Game data: {len(data)} elementos cargados")
        else:
            print(f"❌ Game data falló: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error en game data: {e}")
        return False

    # Test 3: Game state (debería fallar para usuario nuevo)
    try:
        response = requests.get(f"{base_url}/game-state/test-user")
        if response.status_code == 404:
            print("✅ Game state (usuario nuevo): 404 correcto")
        else:
            print(f"⚠️  Game state inesperado: {response.status_code}")
    except Exception as e:
        print(f"❌ Error en game state: {e}")
        return False

    # Test 4: Save game state
    test_game_state = {
        "gold": 1000,
        "day": 1,
        "creatures": [],
        "buildings": [],
        "inventory": [],
        "player_pos": [0, 0]
    }

    try:
        response = requests.post(
            f"{base_url}/game-state/test-user",
            json=test_game_state
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Save game state: {data}")
        else:
            print(f"❌ Save game state falló: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error en save game state: {e}")
        return False

    # Test 5: Load game state (debería funcionar ahora)
    try:
        response = requests.get(f"{base_url}/game-state/test-user")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Load game state: gold={data.get('gold')}")
        else:
            print(f"❌ Load game state falló: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error en load game state: {e}")
        return False

    # Test 6: Settings
    test_settings = {"volume": 0.8, "fullscreen": False}

    try:
        # Save settings
        response = requests.post(
            f"{base_url}/settings/test-user",
            json={"settings": test_settings}
        )
        if response.status_code == 200:
            print("✅ Save settings: OK"
        else:
            print(f"❌ Save settings falló: {response.status_code}")
            return False

        # Load settings
        response = requests.get(f"{base_url}/settings/test-user")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Load settings: {data}")
        else:
            print(f"❌ Load settings falló: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error en settings: {e}")
        return False

    print("=" * 50)
    print("🎉 ¡Todas las pruebas pasaron! Backend funcionando correctamente.")
    return True

def main():
    """Función principal"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1].rstrip('/')
    else:
        # Intentar leer del .env
        env_file = Path(__file__).parent / '.env'
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith('REMOTE_API_URL='):
                        base_url = line.split('=', 1)[1].strip()
                        break
        else:
            print("Uso: python test_backend.py <URL_DEL_BACKEND>")
            print("O configura REMOTE_API_URL en .env")
            sys.exit(1)

    if not base_url:
        print("❌ No se encontró REMOTE_API_URL")
        sys.exit(1)

    success = test_backend(base_url)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()