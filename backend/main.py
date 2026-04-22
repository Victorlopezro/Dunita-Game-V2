import json
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.firebase_client import get_realtime_db
from backend.schemas import GameStatePayload, SettingsPayload


app = FastAPI(
    title="Dunita Game Backend",
    description="Backend para guardar partidas y configuración usando Firebase Realtime DB.",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB = get_realtime_db()

DATA_FILE = Path(__file__).resolve().parents[1] / "dunita_game" / "data" / "game_data.json"


def _get_ref(path: str):
    return DB.reference(path)


def _load_game_data():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"No se encontró {DATA_FILE}")
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


@app.get("/")
def health_check():
    return {"status": "ok", "service": "dunita-game-backend"}


@app.get("/game-state/{user_id}")
def get_game_state(user_id: str):
    ref = _get_ref(f"game_states/{user_id}")
    data = ref.get()

    if data is None:
        raise HTTPException(status_code=404, detail="No game state found")

    return data.get("state", {})


@app.post("/game-state/{user_id}")
def save_game_state(user_id: str, payload: GameStatePayload):
    data = payload.dict()

    ref = _get_ref(f"game_states/{user_id}")
    ref.set({"state": data})

    return {"saved": True, "user_id": user_id}


@app.get("/settings/{user_id}")
def get_settings(user_id: str):
    ref = _get_ref(f"user_settings/{user_id}")
    data = ref.get()

    if data is None:
        raise HTTPException(status_code=404, detail="No settings found")

    return data.get("settings", {})


@app.post("/settings/{user_id}")
def save_settings(user_id: str, payload: SettingsPayload):
    ref = _get_ref(f"user_settings/{user_id}")
    ref.set({"settings": payload.settings})

    return {"saved": True, "user_id": user_id}


@app.get("/game-data")
def get_game_data():
    return _load_game_data()
