"""
Economy Service - Servicio de dominio para lÃ³gica econÃ³mica pura
"""
from typing import Tuple, List, Dict, Optional
from src.domain.entities import Creature, Building, Item, Weapon, GameState

class EconomyService:
    @staticmethod
    def buy_creature(creature_data: Dict, current_gold: int) -> Tuple[bool, str, int, Optional[Creature]]:
        cost = creature_data.get('costeCompra', 0)
        if current_gold < cost:
            return False, f"Fondos insuficientes. Necesitas {cost} Solaris.", current_gold, None

        creature = Creature(
            id=creature_data['id'],
            name=creature_data['nombre'],
            tags=creature_data.get('tags', []),
            daily_feed_cost=creature_data.get('costeAlimentacionDiario', 10),
            weekly_feed_cost=creature_data.get('costeAlimentacionSemanal', 70),
            instance_id=EconomyService._generate_id()
        )
        return True, f"Criatura adquirida: {creature.name}", current_gold - cost, creature

    @staticmethod
    def buy_building(building_data: Dict, current_gold: int) -> Tuple[bool, str, int, Optional[Building]]:
        cost = building_data.get('coste', 0)
        if current_gold < cost:
            return False, f"Fondos insuficientes. Necesitas {cost} Solaris.", current_gold, None

        building = Building(
            id=building_data['id'],
            name=building_data['nombre'],
            cost=cost,
            maintenance_cost=building_data.get('stats', {}).get('mantenimiento', 10),
            capacity=building_data.get('capacidadMaxima', 5),
            allowed_tags=building_data.get('tagEspeciesPermitidas', []),
            assigned_creatures=[],
            instance_id=EconomyService._generate_id()
        )
        return True, f"Edificio adquirido: {building.name}", current_gold - cost, building

    @staticmethod
    def buy_item(item_data: Dict, current_gold: int, inventory_size: int, current_inventory: List[Item]) -> Tuple[bool, str, int, Optional[Item]]:
        cost = item_data.get('coste', 0)
        tipo = item_data.get('tipo', '').upper()

        if current_gold < cost:
            return False, f"Fondos insuficientes. Necesitas {cost} Solaris.", current_gold, None

        if tipo in ['POCION', 'ARMA']:
            if len(current_inventory) >= inventory_size:
                return False, f"Inventario lleno ({len(current_inventory)}/{inventory_size}).", current_gold, None

        if tipo == 'ARMA':
            item = Weapon(
                id=item_data['id'],
                name=item_data['nombre'],
                item_type='ARMA',
                cost=cost,
                damage=item_data.get('daÃ±o', 10),
                range=item_data.get('rango', 100),
                cadence=item_data.get('cadencia', 1.0),
                sprite=item_data.get('sprite', 'weapon_knife'),
                instance_id=EconomyService._generate_id(),
                equipado=False
            )
        else:
            item = Item(
                id=item_data['id'],
                name=item_data['nombre'],
                item_type='POCION' if tipo == 'POCION' else tipo,
                cost=cost,
                instance_id=EconomyService._generate_id(),
                efectos=item_data.get('efectos', [])
            )

        return True, f"{item.name} aÃ±adido al inventario.", current_gold - cost, item

    @staticmethod
    def advance_turn(turn_type: str, creatures: List[Creature], buildings: List[Building],
                    current_gold: int, current_day: int) -> Dict:
        multiplier = 7 if turn_type == 'week' else 1

        feed_cost = 0
        feed_breakdown = []
        for creature in creatures:
            cost = creature.daily_feed_cost * multiplier
            feed_cost += cost
            feed_breakdown.append({'nombre': creature.name, 'coste': cost})

        maint_cost = 0
        maint_breakdown = []
        for building in buildings:
            cost = building.maintenance_cost * multiplier
            maint_cost += cost
            maint_breakdown.append({'nombre': building.name, 'coste': cost})

        total_cost = feed_cost + maint_cost
        new_gold = max(0, current_gold - total_cost)
        new_day = current_day + multiplier

        return {
            'new_gold': new_gold,
            'new_day': new_day,
            'total_cost': total_cost,
            'feed_cost': feed_cost,
            'maint_cost': maint_cost,
            'feed_breakdown': feed_breakdown,
            'maint_breakdown': maint_breakdown,
            'bankrupt': new_gold <= 0
        }

    @staticmethod
    def assign_creature_to_building(creature: Creature, building: Building) -> Tuple[bool, str, Creature, Building]:
        if len(building.assigned_creatures) >= building.capacity:
            return False, f"El recinto estÃ¡ lleno ({len(building.assigned_creatures)}/{building.capacity}).", creature, building

        if building.allowed_tags and not any(tag in building.allowed_tags for tag in creature.tags):
            return False, f"Esta criatura ({', '.join(creature.tags)}) no es compatible con este recinto ({', '.join(building.allowed_tags)}).", creature, building

        updated_creature = creature._replace(building_id=building.instance_id)
        updated_building = building._replace(assigned_creatures=building.assigned_creatures + [creature.instance_id])

        return True, f"{creature.name} asignado a {building.name}.", updated_creature, updated_building

    @staticmethod
    def equip_weapon(instance_id: str, inventory: List[Item]) -> Tuple[bool, str, Optional[Weapon]]:
        weapon = None
        for item in inventory:
            if isinstance(item, Weapon) and item.instance_id == instance_id:
                weapon = item
                break
        if weapon:
            return True, f"Equipado: {weapon.name}", weapon
        return False, "Arma no encontrada", None

    @staticmethod
    def _generate_id() -> str:
        import time
        import random
        return f"{int(time.time() * 1000)}_{random.randint(1000, 9999)}"
