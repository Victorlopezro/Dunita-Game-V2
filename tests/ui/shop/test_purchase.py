from src.ui.ui_manager import ShopUI


class DummyEconomy:
    def __init__(self):
        self.calls = []

    def buy_creature(self, item):
        self.calls.append(('creature', item))
        return True, 'Creature bought'

    def buy_building(self, item):
        self.calls.append(('building', item))
        return True, 'Building bought', {'instance_id': 'building_1'}

    def buy_item(self, item):
        self.calls.append(('item', item))
        return True, 'Item bought'


def test_shop_purchase_building_sets_pending_placement_and_closes():
    economy = DummyEconomy()
    shop = ShopUI(economy, {'creatures': [], 'buildings': [], 'items': []})

    shop.tab = 'buildings'
    shop.selected_item = {'id': 'hut', 'nombre': 'Hut', 'coste': 200}
    shop._on_buy()

    assert shop.pending_building_placement == {'instance_id': 'building_1'}
    assert shop.visible is False
    assert shop.message == 'Building bought'


def test_shop_purchase_without_selection_shows_error_message():
    economy = DummyEconomy()
    shop = ShopUI(economy, {'creatures': [], 'buildings': [], 'items': []})

    shop.tab = 'items'
    shop.selected_item = None
    shop._on_buy()

    assert 'Selecciona un item primero' in shop.message
    assert shop.pending_building_placement is None
