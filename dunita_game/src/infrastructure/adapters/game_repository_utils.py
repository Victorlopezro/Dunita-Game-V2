import json
import os
from typing import Any, Dict

from src.domain.entities import (
    Building,
    Creature,
    GameState,
    Item,
    Position,
    Weapon,
)


def _dict_to_creature(d: Dict[str, Any]) -> Creature:
    return Creature(
        id=d.get('id', ''),
        name=d.get('nombre', ''),
        tags=d.get('tags', []),
        daily_feed_cost=d.get('costeAlimentacionDiario', 10),
        weekly_feed_cost=d.get('costeAlimentacionSemanal', 70),
        building_id=d.get('recinto_id'),
        instance_id=d.get('instance_id', ''),
    )


def _creature_to_dict(c: Creature) -> Dict[str, Any]:
    return {
        'id': c.id,
        'nombre': c.name,
        'tags': c.tags,
        'costeAlimentacionDiario': c.daily_feed_cost,
        'costeAlimentacionSemanal': c.weekly_feed_cost,
        'recinto_id': c.building_id,
        'instance_id': c.instance_id,
    }


def _dict_to_building(d: Dict[str, Any]) -> Building:
    pos = (d.get('tile_x'), d.get('tile_y'))
    position = Position(pos[0], pos[1]) if pos[0] is not None and pos[1] is not None else None
    return Building(
        id=d.get('id', ''),
        name=d.get('nombre', ''),
        cost=d.get('coste', 0),
        maintenance_cost=d.get('mantenimiento', 10),
        capacity=d.get('capacidadMaxima', 5),
        allowed_tags=d.get('tagEspeciesPermitidas', []),
        assigned_creatures=d.get('criaturas_asignadas', []),
        position=position,
        instance_id=d.get('instance_id', ''),
    )


def _building_to_dict(b: Building) -> Dict[str, Any]:
    result = {
        'id': b.id,
        'nombre': b.name,
        'coste': b.cost,
        'mantenimiento': b.maintenance_cost,
        'capacidadMaxima': b.capacity,
        'tagEspeciesPermitidas': b.allowed_tags,
        'criaturas_asignadas': b.assigned_creatures,
        'instance_id': b.instance_id,
    }
    if b.position:
        result['tile_x'] = b.position.x
        result['tile_y'] = b.position.y
    return result


def _dict_to_item(d: Dict[str, Any]) -> Item:
    tipo = d.get('tipo', '')
    if tipo == 'ARMA':
        return Weapon(
            id=d.get('id', ''),
            name=d.get('nombre', ''),
            item_type='ARMA',
            cost=d.get('coste', 0),
            instance_id=d.get('instance_id', ''),
            equipado=d.get('equipado', False),
            damage=d.get('daño', 0),
            range=d.get('rango', 0),
            cadence=d.get('cadencia', 0),
            sprite=d.get('sprite', 'weapon_knife'),
        )
    return Item(
        id=d.get('id', ''),
        name=d.get('nombre', ''),
        item_type=tipo,
        cost=d.get('coste', 0),
        instance_id=d.get('instance_id', ''),
        equipado=d.get('equipado', False),
        efectos=d.get('efectos', []),
    )


def _item_to_dict(i: Item) -> Dict[str, Any]:
    result = {
        'id': i.id,
        'nombre': i.name,
        'tipo': i.item_type,
        'coste': i.cost,
        'instance_id': i.instance_id,
        'equipado': getattr(i, 'equipado', False),
    }
    if getattr(i, 'item_type', '') == 'ARMA':
        result.update(
            {
                'daño': getattr(i, 'damage', 0),
                'rango': getattr(i, 'range', 0),
                'cadencia': getattr(i, 'cadence', 0),
                'sprite': getattr(i, 'sprite', 'weapon_knife'),
            }
        )
    if getattr(i, 'efectos', None) is not None:
        result['efectos'] = getattr(i, 'efectos', [])
    return result


def load_game_state_from_dict(data: Dict[str, Any]) -> GameState:
    return GameState(
        gold=data.get('gold', 25000),
        day=data.get('day', 1),
        creatures=[_dict_to_creature(c) for c in data.get('creatures', [])],
        buildings=[_dict_to_building(b) for b in data.get('buildings', [])],
        inventory=[_dict_to_item(i) for i in data.get('inventory', [])],
        player_pos=Position(
            data.get('player_pos', [0, 0])[0],
            data.get('player_pos', [0, 0])[1],
        ),
        seed=data.get('seed'),
        time_elapsed=data.get('time_elapsed', 0.0),
    )


def game_state_to_dict(state: GameState) -> Dict[str, Any]:
    return {
        'gold': state.gold,
        'day': state.day,
        'creatures': [_creature_to_dict(c) for c in state.creatures],
        'buildings': [_building_to_dict(b) for b in state.buildings],
        'inventory': [_item_to_dict(i) for i in state.inventory],
        'player_pos': [state.player_pos.x, state.player_pos.y],
        'seed': state.seed,
        'time_elapsed': state.time_elapsed,
    }