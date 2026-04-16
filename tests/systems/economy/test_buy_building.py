from src.systems.economy_manager import EconomyManager


def test_buy_building_success_reduces_gold_and_adds_building():
    economy = EconomyManager({'gold': 1000, 'buildings': [], 'creatures': [], 'inventory': []})

    success, message, building = economy.buy_building({
        'id': 'hut',
        'nombre': 'Hut',
        'coste': 500,
        'stats': {'mantenimiento': 20},
        'capacidadMaxima': 4,
        'tagEspeciesPermitidas': ['sand'],
        'sprite': 'hut.png'
    })

    assert success is True
    assert building is not None
    assert economy.gold == 500
    assert len(economy.buildings) == 1
    assert economy.buildings[0]['nombre'] == 'Hut'


def test_buy_building_fails_when_insufficient_funds():
    economy = EconomyManager({'gold': 100, 'buildings': [], 'creatures': [], 'inventory': []})

    success, message, building = economy.buy_building({
        'id': 'hut',
        'nombre': 'Hut',
        'coste': 500
    })

    assert success is False
    assert building is None
    assert economy.gold == 100
