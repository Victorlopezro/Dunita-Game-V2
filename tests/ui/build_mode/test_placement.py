from src.ui.ui_manager import BuildModeUI


class DummyWorld:
    def __init__(self, walkable=True):
        self.buildings_on_map = {}
        self.walkable = walkable
        self.placed = []

    def is_walkable(self, x, y):
        return self.walkable

    def place_building(self, tx, ty, building_instance, size):
        self.placed.append((tx, ty, size))
        return True


class DummyEconomy:
    def __init__(self):
        self.placed = []

    def place_building(self, instance_id, tx, ty):
        self.placed.append((instance_id, tx, ty))


def test_build_mode_updates_ghost_and_places_building_when_valid():
    world = DummyWorld(walkable=True)
    economy = DummyEconomy()
    ui = BuildModeUI(world, economy)

    building = {'instance_id': 'b1', 'stats': {'capacidad': 5}}
    ui.activate(building)
    ui.update_ghost((0, 0), 0, 0)

    assert ui.can_place is True
    assert ui.ghost_pos == (0, 0)
    assert ui.try_place() is True
    assert ui.active is False
    assert economy.placed == [('b1', 0, 0)]


def test_build_mode_cannot_place_when_tile_not_walkable():
    world = DummyWorld(walkable=False)
    economy = DummyEconomy()
    ui = BuildModeUI(world, economy)

    building = {'instance_id': 'b1', 'stats': {'capacidad': 5}}
    ui.activate(building)
    ui.update_ghost((0, 0), 0, 0)

    assert ui.can_place is False
    assert ui.try_place() is False
    assert economy.placed == []
