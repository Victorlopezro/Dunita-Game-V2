import json
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.firebase_client import get_firestore_client
from backend.schemas import GameStatePayload, SettingsPayload

app = FastAPI(
    title="Dunita Game Backend",
    description="Backend para guardar partidas y configuración de Dunita usando Firebase.",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB = get_firestore_client()
GAME_STATE_COLLECTION = "game_states"
SETTINGS_COLLECTION = "user_settings"
DATA_FILE = Path(__file__).resolve().parents[1] / "dunita_game" / "data" / "game_data.json"


def _get_doc(collection: str, document_id: str):
    return DB.collection(collection).document(document_id)


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
    doc = _get_doc(GAME_STATE_COLLECTION, user_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="No game state found for user")
    return doc.to_dict().get("state", {})


@app.post("/game-state/{user_id}")
def save_game_state(user_id: str, payload: GameStatePayload):
    data = payload.dict()
    _get_doc(GAME_STATE_COLLECTION, user_id).set({"state": data})
    return {"saved": True, "user_id": user_id}


@app.get("/settings/{user_id}")
def get_settings(user_id: str):
    doc = _get_doc(SETTINGS_COLLECTION, user_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="No settings found for user")
    return doc.to_dict().get("settings", {})


@app.post("/settings/{user_id}")
def save_settings(user_id: str, payload: SettingsPayload):
    _get_doc(SETTINGS_COLLECTION, user_id).set({"settings": payload.settings})
    return {"saved": True, "user_id": user_id}


@app.get("/game-data")
def get_game_data():
    return _load_game_data()
