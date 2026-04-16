from src.systems.economy_manager import EconomyManager


def test_advance_day_deducts_daily_upkeep_and_increments_day():
    economy = EconomyManager({
        'gold': 100,
        'day': 1,
        'creatures': [
            {'id': 'creature_1', 'nombre': 'Test', 'costeAlimentacionDiario': 10}
        ],
        'buildings': [
            {'id': 'building_1', 'nombre': 'House', 'mantenimiento': 5}
        ],
        'inventory': []
    })

    result = economy.advance_turn('day')

    assert result['new_gold'] == 85
    assert result['new_day'] == 2
    assert result['total_cost'] == 15
    assert result['bankrupt'] is False


def test_advance_week_with_insufficient_funds_sets_gold_to_zero():
    economy = EconomyManager({
        'gold': 10,
        'day': 5,
        'creatures': [
            {'id': 'creature_1', 'nombre': 'Test', 'costeAlimentacionDiario': 10}
        ],
        'buildings': [
            {'id': 'building_1', 'nombre': 'House', 'mantenimiento': 5}
        ],
        'inventory': []
    })

    result = economy.advance_turn('week')

    assert result['new_gold'] == 0
    assert result['new_day'] == 12
    assert result['bankrupt'] is True
