import pytest
from src.states.loading_screen import LoadingScreenState
from src.infrastructure.config.config import GameState


class DummyEngine:
    def __init__(self):
        self.screen = None
        self.settings = {}
        self.game_data = {}
        self.state_changes = []

    def change_state(self, state, **kwargs):
        self.state_changes.append((state, kwargs))


def test_loading_screen_transitions_after_exact_duration():
    engine = DummyEngine()
    state = LoadingScreenState(engine)
    state.on_enter(mode='new')

    state.update(3.5)
    assert not state.done
    assert engine.state_changes == []

    state.update(3.5)
    assert state.done is True
    assert engine.state_changes == [(GameState.GAMEPLAY, {})]


def test_loading_screen_transitions_with_large_dt():
    engine = DummyEngine()
    state = LoadingScreenState(engine)
    state.on_enter(mode='load')

    state.update(10.0)
    assert state.done is True
    assert engine.state_changes == [(GameState.GAMEPLAY, {})]
