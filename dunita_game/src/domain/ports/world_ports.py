"""
Domain Ports - Interfaces para dependencias externas
"""
from abc import ABC, abstractmethod
from typing import List, Tuple
from src.domain.entities import Position

class WorldServicePort(ABC):
    @abstractmethod
    def is_walkable(self, x: int, y: int) -> bool:
        pass

    @abstractmethod
    def place_building(self, x: int, y: int, building_id: str) -> bool:
        pass

class EntitySpawnerPort(ABC):
    @abstractmethod
    def spawn_enemy(self, player_pos: Position, day: int) -> Tuple[float, float]:
        pass

    @abstractmethod
    def spawn_visitor(self, building_positions: List[Position]) -> Tuple[float, float]:
        pass