from unittest.mock import MagicMock, patch
from src.systems.audio_manager import AudioManager


def make_audio_manager():
    manager = AudioManager.__new__(AudioManager)
    manager._initialized = True
    manager._use_generated = False
    manager._current_track = None
    manager._current_state = None
    manager._bgm_tracks = {
        'main_menu': '/tmp/fake_menu.mp3',
        'gameplay': '/tmp/fake_game.mp3'
    }
    return manager


@patch('src.systems.audio_manager.pygame.mixer.music')
def test_play_bgm_loads_and_plays_file(mock_music):
    manager = make_audio_manager()
    manager.play_bgm('main_menu')

    mock_music.load.assert_called_once_with('/tmp/fake_menu.mp3')
    mock_music.set_volume.assert_called_once()
    mock_music.play.assert_called_once_with(-1)


@patch('src.systems.audio_manager.pygame.mixer.music')
def test_play_bgm_does_not_reload_same_track(mock_music):
    manager = make_audio_manager()
    manager._current_track = '/tmp/fake_menu.mp3'
    manager.play_bgm('main_menu')

    mock_music.load.assert_not_called()
    mock_music.play.assert_not_called()


@patch('src.systems.audio_manager.pygame.mixer.music')
def test_play_bgm_stops_when_state_unknown(mock_music):
    manager = make_audio_manager()
    manager._bgm_tracks = {}
    manager.play_bgm('unknown_state')

    mock_music.stop.assert_called_once()
