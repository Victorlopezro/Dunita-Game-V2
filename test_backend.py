#!/usr/bin/env python3
"""
Script de prueba para el backend de Dunita Game (Realtime DB)
"""

import requests
import sys
from pathlib import Path


def test_backend(base_url: str):
    print(f"Probando backend en: {base_url}")
    print("=" * 50)

    # 1. Health
    try:
        r = requests.get(f"{base_url}/")
        assert r.status_code == 200
        print("OK Health:", r.json())
    except Exception as e:
        print("FAIL Health:", e)
        return False

    # 2. Game data
    try:
        r = requests.get(f"{base_url}/game-data")
        assert r.status_code == 200
        print("OK Game data:", len(r.json()))
    except Exception as e:
        print("FAIL Game data:", e)
        return False

    # 3. Game state (new user)
    try:
        r = requests.get(f"{base_url}/game-state/test-user")
        if r.status_code == 404:
            print("OK New user 404")
        else:
            print("WARN Unexpected:", r.status_code)
    except Exception as e:
        print("FAIL Game state:", e)
        return False

    # 4. Save game state
    payload = {
        "gold": 1000,
        "day": 1,
        "creatures": [],
        "buildings": [],
        "inventory": [],
        "player_pos": [0, 0]
    }

    try:
        r = requests.post(f"{base_url}/game-state/test-user", json=payload)
        assert r.status_code == 200
        print("OK Save game state:", r.json())
    except Exception as e:
        print("FAIL Save game state:", e)
        return False

    # 5. Load game state
    try:
        r = requests.get(f"{base_url}/game-state/test-user")
        assert r.status_code == 200
        data = r.json()
        print("OK Load game state: gold =", data.get("gold"))
    except Exception as e:
        print("FAIL Load game state:", e)
        return False

    # 6. Settings
    settings = {"volume": 0.8, "fullscreen": False}

    try:
        r = requests.post(
            f"{base_url}/settings/test-user",
            json={"settings": settings}
        )
        assert r.status_code == 200
        print("OK Save settings")

        r = requests.get(f"{base_url}/settings/test-user")
        assert r.status_code == 200
        print("OK Load settings:", r.json())

    except Exception as e:
        print("FAIL Settings:", e)
        return False

    print("=" * 50)
    print("ALL TESTS PASSED")
    return True


def main():
    if len(sys.argv) > 1:
        base_url = sys.argv[1].rstrip('/')
    else:
        env_file = Path(__file__).parent / '.env'
        base_url = None

        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith('REMOTE_API_URL='):
                        base_url = line.split('=', 1)[1].strip()
                        break

        if not base_url:
            print("Usage: python test_backend.py <URL>")
            sys.exit(1)

    success = test_backend(base_url)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
