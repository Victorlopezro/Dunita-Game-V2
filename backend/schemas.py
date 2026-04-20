from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class CreaturePayload(BaseModel):
    id: str
    nombre: str
    tags: List[str]
    costeAlimentacionDiario: int
    costeAlimentacionSemanal: int
    recinto_id: Optional[str] = None
    instance_id: str = ""


class BuildingPayload(BaseModel):
    id: str
    nombre: str
    coste: int
    mantenimiento: int
    capacidadMaxima: int
    tagEspeciesPermitidas: List[str]
    criaturas_asignadas: List[str]
    instance_id: str = ""
    tile_x: Optional[int] = None
    tile_y: Optional[int] = None


class ItemPayload(BaseModel):
    id: str
    nombre: str
    tipo: str
    coste: int
    instance_id: str = ""
    equipado: bool = False
    efectos: Optional[List[str]] = []
    daño: Optional[int] = 0
    rango: Optional[float] = 0.0
    cadencia: Optional[float] = 0.0
    sprite: Optional[str] = None


class GameStatePayload(BaseModel):
    gold: int
    day: int
    creatures: List[CreaturePayload]
    buildings: List[BuildingPayload]
    inventory: List[ItemPayload]
    player_pos: List[int]
    seed: Optional[int] = None
    time_elapsed: float = 0.0


class SettingsPayload(BaseModel):
    settings: Dict[str, Any]
