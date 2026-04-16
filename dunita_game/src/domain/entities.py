"""
Domain Entities - Entidades de negocio puras e inmutables
"""
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass(frozen=True)
class Position:
    x: float
    y: float

@dataclass(frozen=True)
class Creature:
    id: str
    name: str
    tags: List[str]
    daily_feed_cost: int
    weekly_feed_cost: int
    building_id: Optional[str] = None
    instance_id: str = ""

@dataclass(frozen=True)
class Building:
    id: str
    name: str
    cost: int
    maintenance_cost: int
    capacity: int
    allowed_tags: List[str]
    assigned_creatures: List[str]
    position: Optional[Position] = None
    instance_id: str = ""

@dataclass(frozen=True)
class Item:
    id: str
    name: str
    item_type: str  # 'ARMA', 'POCION', etc.
    cost: int
    instance_id: str = ""
    equipado: bool = False
    efectos: List[str] = field(default_factory=list)

@dataclass(frozen=True)
class Weapon(Item):
    damage: int = 0
    range: float = 0.0
    cadence: float = 0.0
    sprite: str = ""

@dataclass(frozen=True)
class GameState:
    gold: int
    day: int
    creatures: List[Creature]
    buildings: List[Building]
    inventory: List[Item]
    player_pos: Position
    seed: Optional[int] = None
    time_elapsed: float = 0.0