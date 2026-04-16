from src.systems.world import WorldMap, TileType


def test_place_building_succeeds_on_empty_sand_tiles():
    world = WorldMap(seed=123)
    world.get_tile = lambda tx, ty: TileType.SAND
    world.buildings_on_map = {}

    building = {'id': 'hut'}
    success = world.place_building(0, 0, building, size=2)

    assert success is True
    assert building['tile_x'] == 0
    assert building['tile_y'] == 0
    assert building['size'] == 2
    assert (0, 0) in world.buildings_on_map
    assert (1, 1) in world.buildings_on_map


def test_place_building_fails_if_space_occupied():
    world = WorldMap(seed=123)
    world.get_tile = lambda tx, ty: TileType.SAND
    world.buildings_on_map = {(0, 0): {'id': 'existing'}}

    success = world.place_building(0, 0, {'id': 'hut'}, size=2)
    assert success is False


def test_place_building_fails_if_tile_is_rock():
    world = WorldMap(seed=123)
    world.get_tile = lambda tx, ty: TileType.ROCK if (tx, ty) == (1, 1) else TileType.SAND
    world.buildings_on_map = {}

    success = world.place_building(0, 0, {'id': 'hut'}, size=2)
    assert success is False
