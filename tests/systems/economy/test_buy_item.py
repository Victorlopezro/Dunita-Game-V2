from src.systems.economy_manager import EconomyManager


def test_buy_item_potion_stores_in_inventory_and_reduces_gold():
    economy = EconomyManager({'gold': 100, 'inventory': [], 'buildings': [], 'creatures': []})

    success, message = economy.buy_item({
        'id': 'potion_1',
        'nombre': 'Potion',
        'coste': 20,
        'tipo': 'POCION',
        'efectos': ['heal']
    })

    assert success is True
    assert economy.gold == 80
    assert len(economy.inventory) == 1
    assert economy.inventory[0]['id'] == 'potion_1'


def test_buy_item_fails_if_inventory_full_for_weapon():
    economy = EconomyManager({'gold': 100, 'inventory': [{}] * 8, 'buildings': [], 'creatures': []})

    success, message = economy.buy_item({
        'id': 'sword_1',
        'nombre': 'Sword',
        'coste': 10,
        'tipo': 'ARMA'
    })

    assert success is False
    assert 'Inventario lleno' in message
    assert economy.gold == 100


def test_buy_item_unknown_type_deducts_gold_without_storing_item():
    economy = EconomyManager({'gold': 50, 'inventory': [], 'buildings': [], 'creatures': []})

    success, message = economy.buy_item({
        'id': 'artifact',
        'nombre': 'Artifact',
        'coste': 10,
        'tipo': 'OTRO'
    })

    assert success is True
    assert economy.gold == 40
    assert len(economy.inventory) == 0
