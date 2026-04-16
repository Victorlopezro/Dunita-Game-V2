"""
Tests for the refactored code
"""
import pytest
from src.domain.services.economy_service import EconomyService
from src.domain.entities import Creature, Building

def test_buy_creature_success():
    creature_data = {
        'id': 'sandworm',
        'nombre': 'Sandworm',
        'costeCompra': 1000,
        'tags': ['large'],
        'costeAlimentacionDiario': 50
    }
    current_gold = 2000
    
    success, message, new_gold, creature = EconomyService.buy_creature(creature_data, current_gold)
    
    assert success == True
    assert new_gold == 1000
    assert creature.name == 'Sandworm'
    assert creature.daily_feed_cost == 50

def test_advance_turn():
    creatures = [Creature(id='1', name='Test', tags=[], daily_feed_cost=10, weekly_feed_cost=70)]
    buildings = [Building(id='1', name='Test', cost=0, maintenance_cost=5, capacity=5, allowed_tags=[], assigned_creatures=[])]
    current_gold = 100
    current_day = 1
    
    result = EconomyService.advance_turn('day', creatures, buildings, current_gold, current_day)
    
    assert result['new_gold'] == 85  # 100 - 10 - 5
    assert result['new_day'] == 2
    assert result['total_cost'] == 15