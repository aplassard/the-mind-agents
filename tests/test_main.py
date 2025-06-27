import pytest
import yaml
from unittest.mock import patch, MagicMock
from pathlib import Path

from themind.main import main
from themind.agents import RandomAgent, PerfectAgent


def create_test_config(tmp_path: Path, config_data: dict) -> str:
    """Helper function to create a temporary YAML config file."""
    config_file = tmp_path / "test_config.yaml"
    with open(config_file, 'w') as f:
        yaml.dump(config_data, f)
    return str(config_file)


@patch('themind.main.argparse.ArgumentParser')
@patch('themind.main.Team')
def test_successful_agent_creation(mock_team, mock_argparse, tmp_path):
    """
    Tests that the main script correctly creates agents from a valid config file.
    """
    # Arrange
    config_data = {
        "game_name": "Test Game",
        "agents": [
            {"type": "RandomAgent", "name": "Randy"},
            {"type": "PerfectAgent", "name": "Percy"},
        ],
    }
    config_file_path = create_test_config(tmp_path, config_data)

    # Mock argparse to return the path to our test config
    mock_parser = MagicMock()
    mock_parser.parse_args.return_value.config_file = config_file_path
    mock_argparse.return_value = mock_parser

    # Act
    main()

    # Assert
    mock_team.assert_called_once()
    created_agents = mock_team.call_args[0][0]

    assert len(created_agents) == 2
    assert isinstance(created_agents[0], RandomAgent)
    assert created_agents[0].name == "Randy"
    assert isinstance(created_agents[1], PerfectAgent)
    assert created_agents[1].name == "Percy"


@patch('themind.main.argparse.ArgumentParser')
def test_unknown_agent_type(mock_argparse, tmp_path):
    """
    Tests that the main script raises a ValueError for an unknown agent type.
    """
    # Arrange
    config_data = {
        "agents": [{"type": "UnknownAgent", "name": "MysteryMan"}]
    }
    config_file_path = create_test_config(tmp_path, config_data)

    # Mock argparse
    mock_parser = MagicMock()
    mock_parser.parse_args.return_value.config_file = config_file_path
    mock_argparse.return_value = mock_parser

    # Act & Assert
    with pytest.raises(ValueError, match="Unknown agent type: UnknownAgent"):
        main()
