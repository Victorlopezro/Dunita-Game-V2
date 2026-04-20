"""
Infrastructure Adapters - Implementaciones concretas de los ports
"""
import json
import os
from typing import Optional
from src.application.ports.game_repository import GameRepository
from src.domain.entities import GameState
from src.infrastructure.adapters.game_repository_utils import (
    game_state_to_dict,
    load_game_state_from_dict,
)

class JsonGameRepository(GameRepository):
    def __init__(self, save_file: str, settings_file: str, data_file: str):
        self.save_file = save_file
        self.settings_file = settings_file
        self.data_file = data_file

    def load_game_state(self) -> Optional[GameState]:
        try:
            with open(self.save_file, 'r') as f:
                data = json.load(f)
            return load_game_state_from_dict(data)
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def save_game_state(self, state: GameState):
        data = game_state_to_dict(state)
        os.makedirs(os.path.dirname(self.save_file), exist_ok=True)
        with open(self.save_file, 'w') as f:
            json.dump(data, f, indent=2)

    def load_settings(self) -> dict:
        try:
            with open(self.settings_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_settings(self, settings: dict):
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f, indent=2)

    def load_game_data(self) -> dict:
        with open(self.data_file, 'r', encoding='utf-8') as f:
            return json.load(f)


