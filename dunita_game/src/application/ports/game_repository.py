"""
Application Ports - Interfaces para repositorios y servicios externos
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities import GameState, Creature, Building, Item, Position

class GameRepository(ABC):
    @abstractmethod
    def load_game_state(self) -> Optional[GameState]:
        pass

    @abstractmethod
    def save_game_state(self, state: GameState):
        pass

    @abstractmethod
    def load_settings(self) -> dict:
        pass

    @abstractmethod
    def save_settings(self, settings: dict):
        pass

    @abstractmethod
    def load_game_data(self) -> dict:
        pass