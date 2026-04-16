"""
Economy Manager Adapter - Adapter para mantener compatibilidad con el cÃ³digo existente
"""
from dataclasses import replace
from src.application.use_cases.economy_use_cases import BuyCreatureUseCase, AdvanceTurnUseCase, AssignCreatureUseCase
from src.infrastructure.adapters.json_game_repository import JsonGameRepository
from src.domain.entities import GameState, Weapon

class EconomyManagerAdapter:
    def __init__(self, repository: JsonGameRepository, initial_state: dict = None):
        self.repository = repository
        self._callbacks = []
        self.pending_mercenary_spawn = None
        self._initial_state = initial_state
        if self._initial_state is not None:
            self._current_state = self._build_state_from_dict(self._initial_state)
            self._save_state(self._current_state)
        else:
            self._current_state = self.repository.load_game_state()
            if self._current_state is None:
                # No saved state and no initial state, create default
                self._current_state = self._build_state_from_dict({
                    'gold': 1000,
                    'day': 1,
                    'creatures': [],
                    'buildings': [],
                    'inventory': [],
                    'player_pos': [0, 0],
                })
                self._save_state(self._current_state)

    def _build_state_from_dict(self, data: dict):
        from src.domain.entities import Creature, Building, Item, Weapon, GameState, Position

        creatures = [Creature(
            id=c.get('id', ''),
            name=c.get('nombre', ''),
            tags=c.get('tags', []),
            daily_feed_cost=c.get('costeAlimentacionDiario', 10),
            weekly_feed_cost=c.get('costeAlimentacionSemanal', 70),
            building_id=c.get('recinto_id'),
            instance_id=c.get('instance_id', '')
        ) for c in data.get('creatures', [])]

        buildings = [Building(
            id=b.get('id', ''),
            name=b.get('nombre', ''),
            cost=b.get('coste', 0),
            maintenance_cost=b.get('mantenimiento', 10),
            capacity=b.get('capacidadMaxima', 5),
            allowed_tags=b.get('tagEspeciesPermitidas', []),
            assigned_creatures=b.get('criaturas_asignadas', []),
            position=Position(b.get('tile_x'), b.get('tile_y')) if b.get('tile_x') is not None and b.get('tile_y') is not None else None,
            instance_id=b.get('instance_id', '')
        ) for b in data.get('buildings', [])]

        inventory = []
        for i in data.get('inventory', []):
            if i.get('tipo') == 'ARMA':
                inventory.append(Weapon(
                    id=i.get('id', ''),
                    name=i.get('nombre', ''),
                    item_type='ARMA',
                    cost=i.get('coste', 0),
                    instance_id=i.get('instance_id', ''),
                    equipado=i.get('equipado', False),
                    damage=i.get('daño', 0),
                    range=i.get('rango', 0),
                    cadence=i.get('cadencia', 0),
                    sprite=i.get('sprite', 'weapon_knife')
                ))
            else:
                inventory.append(Item(
                    id=i.get('id', ''),
                    name=i.get('nombre', ''),
                    item_type=i.get('tipo', ''),
                    cost=i.get('coste', 0),
                    instance_id=i.get('instance_id', ''),
                    equipado=i.get('equipado', False),
                    efectos=i.get('efectos', [])
                ))

        pos = data.get('player_pos', [0, 0])
        return GameState(
            gold=data.get('gold', 0),
            day=data.get('day', 1),
            creatures=creatures,
            buildings=buildings,
            inventory=inventory,
            player_pos=Position(pos[0], pos[1]),
            seed=data.get('seed'),
            time_elapsed=data.get('time_elapsed', 0.0)
        )

    def _get_state(self):
        if self._current_state is not None:
            return self._current_state
        self._current_state = self.repository.load_game_state()
        if self._current_state is None and self._initial_state is not None:
            self._current_state = self._build_state_from_dict(self._initial_state)
            self._save_state(self._current_state)
        return self._current_state

    def _save_state(self, state):
        self.repository.save_game_state(state)
        self._current_state = state

    @property
    def gold(self):
        state = self._get_state()
        return state.gold if state else 0
    
    @gold.setter
    def gold(self, value):
        state = self._get_state()
        if state:
            new_state = replace(state, gold=max(0, int(value)))
            self._save_state(new_state)
    
    @property
    def day(self):
        state = self._get_state()
        return state.day if state else 1
    
    @property
    def creatures(self):
        state = self._get_state()
        return [self._creature_to_dict(c) for c in state.creatures] if state else []
    
    @property
    def buildings(self):
        state = self._get_state()
        return [self._building_to_dict(b) for b in state.buildings] if state else []
    
    @property
    def inventory(self):
        state = self._get_state()
        return [self._item_to_dict(i) for i in state.inventory] if state else []
    
    def can_afford(self, cost):
        return self.gold >= cost
    
    def buy_creature(self, creature_data):
        success, message = BuyCreatureUseCase(self.repository).execute(creature_data)
        return success, message
    
    def buy_building(self, building_data):
        cost = building_data.get('coste', 0)
        if self.gold < cost:
            return False, f"Fondos insuficientes. Necesitas {cost} Solaris.", None

        from src.domain.services.economy_service import EconomyService
        success, message, new_gold, building = EconomyService.buy_building(building_data, self.gold)
        if success and building:
            state = self._get_state()
            if state:
                new_state = replace(state, gold=new_gold, buildings=state.buildings + [building])
                self._save_state(new_state)
                self._notify(f"Edificio adquirido: {building.name}")
                return True, message, self._building_to_dict(building)
        return False, message, None
    
    def buy_item(self, item_data):
        from src.infrastructure.config.config import INVENTORY_SIZE
        from src.domain.services.economy_service import EconomyService
        state = self._get_state()
        current_inventory = state.inventory if state else []
        tipo = item_data.get('tipo', '').upper()

        if tipo in ['RECLUTA', 'MERCENARIO']:
            if self.gold < item_data.get('coste', 0):
                return False, f"Fondos insuficientes. Necesitas {item_data.get('coste', 0)} Solaris."
            self.pending_mercenary_spawn = tipo
            self.gold -= item_data.get('coste', 0)
            return True, f"{item_data.get('nombre', 'Recluta')} contratado."

        success, message, new_gold, item = EconomyService.buy_item(item_data, self.gold, INVENTORY_SIZE, current_inventory)
        if success and item and state:
            new_state = replace(state, gold=new_gold, inventory=state.inventory + [item])
            self._save_state(new_state)
            return True, message
        return False, message
    
    def assign_creature_to_building(self, creature_instance_id, building_instance_id):
        success, message = AssignCreatureUseCase(self.repository).execute(creature_instance_id, building_instance_id)
        return success, message

    def equip_weapon(self, instance_id: str):
        from dataclasses import replace
        from src.domain.services.economy_service import EconomyService
        state = self._get_state()
        if not state:
            return False, "Arma no encontrada", None

        success, message, weapon = EconomyService.equip_weapon(instance_id, state.inventory)
        if not success:
            return False, message, None

        updated_inventory = []
        for item in state.inventory:
            if isinstance(item, Weapon):
                if item.instance_id == instance_id:
                    updated_inventory.append(replace(item, equipado=True))
                else:
                    updated_inventory.append(replace(item, equipado=False))
            else:
                updated_inventory.append(item)

        self._save_state(replace(state, inventory=updated_inventory))
        return True, message, weapon

    def use_item(self, instance_id: str):
        state = self._get_state()
        if not state:
            return False, "Ítem no encontrado"

        updated_inventory = []
        item_used = None
        for item in state.inventory:
            if item.instance_id == instance_id and item_used is None:
                item_used = item
                continue
            updated_inventory.append(item)

        if item_used is None:
            return False, "Ítem no encontrado"

        self._save_state(replace(state, inventory=updated_inventory))
        return True, f"Usaste: {item_used.name}"

    def advance_turn(self, turn_type='day'):
        result = AdvanceTurnUseCase(self.repository).execute(turn_type)
        self._notify(f"Turno avanzado: -{result.get('total_cost', 0)} Solaris")
        return result
    
    def place_building(self, instance_id, tile_x, tile_y):
        # Update building position
        state = self.repository.load_game_state()
        if state:
            new_buildings = []
            for b in state.buildings:
                if b.instance_id == instance_id:
                    from src.domain.entities import Position
                    new_b = replace(b, position=Position(tile_x, tile_y))
                    new_buildings.append(new_b)
                else:
                    new_buildings.append(b)
            new_state = replace(state, buildings=new_buildings)
            self._save_state(new_state)
            return True
        return False

    def get_summary(self):
        state = self.repository.load_game_state()
        if not state:
            return {
                'gold': 0,
                'day': 1,
                'num_creatures': 0,
                'num_buildings': 0,
                'inventory_count': 0,
                'inventory_max': 0,
                'daily_upkeep': 0,
            }

        daily_upkeep = sum(c.daily_feed_cost for c in state.creatures) + sum(b.maintenance_cost for b in state.buildings)
        return {
            'gold': state.gold,
            'day': state.day,
            'num_creatures': len(state.creatures),
            'num_buildings': len(state.buildings),
            'inventory_count': len(state.inventory),
            'inventory_max': 8,
            'daily_upkeep': daily_upkeep,
        }

    def add_callback(self, callback):
        self._callbacks.append(callback)

    def _notify(self, message):
        for cb in self._callbacks:
            try:
                cb(message)
            except Exception:
                pass

    def _creature_to_dict(self, c):
        return {
            'id': c.id,
            'nombre': c.name,
            'tags': c.tags,
            'costeAlimentacionDiario': c.daily_feed_cost,
            'costeAlimentacionSemanal': c.weekly_feed_cost,
            'recinto_id': c.building_id,
            'instance_id': c.instance_id
        }

    def _building_to_dict(self, b):
        d = {
            'id': b.id,
            'nombre': b.name,
            'coste': b.cost,
            'mantenimiento': b.maintenance_cost,
            'capacidadMaxima': b.capacity,
            'tagEspeciesPermitidas': b.allowed_tags,
            'criaturas_asignadas': b.assigned_creatures,
            'instance_id': b.instance_id
        }
        if b.position:
            d['tile_x'] = b.position.x
            d['tile_y'] = b.position.y
        return d
    
    def _item_to_dict(self, i):
        result = {
            'id': i.id,
            'nombre': i.name,
            'tipo': i.item_type,
            'coste': i.cost,
            'instance_id': i.instance_id,
            'equipado': getattr(i, 'equipado', False),
        }
        if i.item_type == 'ARMA':
            result.update({
                'daño': getattr(i, 'damage', 0),
                'rango': getattr(i, 'range', 0),
                'cadencia': getattr(i, 'cadence', 0),
                'sprite': getattr(i, 'sprite', 'weapon_knife')
            })
        if getattr(i, 'efectos', None) is not None:
            result['efectos'] = getattr(i, 'efectos', [])
        return result
