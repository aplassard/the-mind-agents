import pytest
import os
import json
from unittest.mock import patch, MagicMock
from themind.team import Team
from themind.agents import PerfectAgent


@pytest.fixture
def agents():
    """Fixture for creating a list of agents."""
    return [
        PerfectAgent(name="Agent 1"),
        PerfectAgent(name="Agent 2"),
    ]


def test_team_initialization(agents):
    """Tests that the Team class is initialized correctly."""
    # Arrange
    num_games = 5

    # Act
    team = Team(agents, num_games)

    # Assert
    assert team.agents == agents
    assert team.num_games == num_games
    assert os.path.isdir(team.results_dir)


@patch('themind.team.Game')
def test_play_games(mock_game, agents):
    """Tests that the play_games method plays the correct number of games."""
    # Arrange
    num_games = 3
    team = Team(agents, num_games)

    # Act
    team.play_games()

    # Assert
    assert mock_game.call_count == num_games


@patch('themind.team.Game')
def test_save_game_results(mock_game, agents, tmp_path):
    """Tests that the game results are saved correctly."""
    # Arrange
    num_games = 1
    team = Team(agents, num_games)
    team.results_dir = tmp_path

    # Mock the game and its levels/turns
    mock_game_instance = MagicMock()
    mock_level = MagicMock()
    mock_turn = MagicMock()
    mock_turn.last_played_card = 10
    mock_turn.player_who_played = "Agent 1"
    mock_turn.played_card = 12
    mock_turn.correct_decision = True
    mock_turn.player_hands = {"Agent 1": [12, 25], "Agent 2": [15, 30]}
    mock_turn.recommended_actions = {
        "Agent 1": MagicMock(time_to_wait=2),
        "Agent 2": MagicMock(time_to_wait=5),
    }
    mock_level.turns = [mock_turn]
    mock_level.level_number = 1
    mock_game_instance.levels = [mock_level]
    mock_game.return_value = mock_game_instance

    # Act
    team.play_games()

    # Assert
    game_dir = tmp_path / "1"
    assert os.path.isdir(game_dir)

    level_file = game_dir / "1.json"
    assert os.path.isfile(level_file)

    with open(level_file, 'r') as f:
        saved_data = json.load(f)

    assert len(saved_data) == 1
    turn_data = saved_data[0]
    assert turn_data["Previous-card"] == 10
    assert turn_data["Acting-player"] == "Agent 1"
    assert turn_data["Card played"] == 12
    assert turn_data["Seconds waited"] == 2
    assert turn_data["Correct decision"] is True
    assert turn_data["Agent 1-hand"] == [12, 25]
    assert turn_data["Agent 1-lowest-card"] == 12
    assert turn_data["Agent 1-seconds"] == 2
    assert turn_data["Agent 2-hand"] == [15, 30]
    assert turn_data["Agent 2-lowest-card"] == 15
    assert turn_data["Agent 2-seconds"] == 5
