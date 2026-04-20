import requests
from requests.exceptions import RequestException
from typing import Optional

from src.application.ports.game_repository import GameRepository
from src.domain.entities import GameState
from src.infrastructure.adapters.json_game_repository import JsonGameRepository
from src.infrastructure.adapters.game_repository_utils import (
    game_state_to_dict,
    load_game_state_from_dict,
)


class RemoteGameRepository(GameRepository):
    def __init__(self, remote_api_url: str, user_id: str, fallback: JsonGameRepository):
        self.remote_api_url = remote_api_url.rstrip('/')
        self.user_id = user_id
        self.fallback = fallback
        self.session = requests.Session()

    def _remote_get(self, path: str):
        try:
            url = f"{self.remote_api_url}/{path.lstrip('/')}"
            response = self.session.get(url, timeout=8.0)
            response.raise_for_status()
            return response.json()
        except RequestException:
            return None

    def _remote_post(self, path: str, data: dict) -> bool:
        try:
            url = f"{self.remote_api_url}/{path.lstrip('/')}"
            response = self.session.post(url, json=data, timeout=8.0)
            response.raise_for_status()
            return True
        except RequestException:
            return False

    def load_game_state(self) -> Optional[GameState]:
        remote_data = self._remote_get(f"game-state/{self.user_id}")
        if isinstance(remote_data, dict):
            try:
                return load_game_state_from_dict(remote_data)
            except Exception:
                pass
        return self.fallback.load_game_state()

    def save_game_state(self, state: GameState):
        payload = game_state_to_dict(state)
        self._remote_post(f"game-state/{self.user_id}", payload)
        self.fallback.save_game_state(state)

    def load_settings(self) -> dict:
        remote_data = self._remote_get(f"settings/{self.user_id}")
        if isinstance(remote_data, dict):
            return remote_data
        return self.fallback.load_settings()

    def save_settings(self, settings: dict):
        self._remote_post(f"settings/{self.user_id}", {"settings": settings})
        self.fallback.save_settings(settings)

    def load_game_data(self) -> dict:
        remote_data = self._remote_get("game-data")
        if isinstance(remote_data, dict) and remote_data:
            return remote_data
        return self.fallback.load_game_data()
