"""
Use Cases - Casos de uso de la aplicación
"""
from typing import Tuple, Dict
from src.domain.services.economy_service import EconomyService
from src.application.ports.game_repository import GameRepository
from src.domain.entities import GameState

class BuyCreatureUseCase:
    def __init__(self, repository: GameRepository):
        self.repository = repository

    def execute(self, creature_data: Dict) -> Tuple[bool, str]:
        state = self.repository.load_game_state()
        if not state:
            return False, "No game state loaded"

        success, message, new_gold, creature = EconomyService.buy_creature(creature_data, state.gold)
        if success and creature:
            new_state = state._replace(gold=new_gold, creatures=state.creatures + [creature])
            self.repository.save_game_state(new_state)
        return success, message

class AdvanceTurnUseCase:
    def __init__(self, repository: GameRepository):
        self.repository = repository

    def execute(self, turn_type: str) -> Dict:
        state = self.repository.load_game_state()
        if not state:
            return {'error': 'No game state loaded'}

        result = EconomyService.advance_turn(turn_type, state.creatures, state.buildings, state.gold, state.day)
        new_state = state._replace(gold=result['new_gold'], day=result['new_day'])
        self.repository.save_game_state(new_state)
        return result

class AssignCreatureUseCase:
    def __init__(self, repository: GameRepository):
        self.repository = repository

    def execute(self, creature_instance_id: str, building_instance_id: str) -> Tuple[bool, str]:
        state = self.repository.load_game_state()
        if not state:
            return False, "No game state loaded"

        creature = next((c for c in state.creatures if c.instance_id == creature_instance_id), None)
        building = next((b for b in state.buildings if b.instance_id == building_instance_id), None)

        if not creature or not building:
            return False, "Criatura o edificio no encontrado"

        success, message, new_creature, new_building = EconomyService.assign_creature_to_building(creature, building)
        if success:
            new_creatures = [new_creature if c.instance_id == creature_instance_id else c for c in state.creatures]
            new_buildings = [new_building if b.instance_id == building_instance_id else b for b in state.buildings]
            new_state = state._replace(creatures=new_creatures, buildings=new_buildings)
            self.repository.save_game_state(new_state)
        return success, message