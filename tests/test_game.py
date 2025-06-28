import pytest
from unittest.mock import patch, MagicMock

from themind.game.game import Deck, Game
from themind.agents.agents import DummyAgent, FastAgent


def test_deck_creation():
    """Tests that the deck is created with 100 unique cards."""
    deck = Deck()
    assert len(deck.cards) == 100
    assert len(set(deck.cards)) == 100
    assert min(deck.cards) == 1
    assert max(deck.cards) == 100


def test_deck_shuffle():
    """Tests that the deck can be shuffled."""
    deck1 = Deck()
    deck2 = Deck()
    # It's statistically very unlikely for two shuffled decks to be identical
    assert deck1.cards != deck2.cards


def test_deck_deal():
    """Tests that dealing cards works correctly."""
    deck = Deck()
    hand = deck.deal(5)
    assert len(hand) == 5
    assert len(deck.cards) == 95


def test_agent_receive_hand():
    """Tests that an agent receives and sorts its hand."""
    agent = DummyAgent(name="test_agent")
    hand = [5, 2, 8]
    agent.receive_hand(hand)
    assert agent.hand == [2, 5, 8]


@patch('themind.game.game.Deck.deal')
def test_game_level_success(mock_deal: MagicMock):
    """Tests a successful playthrough of a level."""
    # Arrange
    players = [DummyAgent(name="p1"), DummyAgent(name="p2")]
    game = Game(players)
    game.current_level_number = 1

    # Mock the hands dealt to players
    mock_deal.side_effect = [[10], [20]]

    # Act
    game.play_level()

    # Assert
    assert not game.game_over
    assert game.current_level_number == 2
    assert len(game.levels) == 1
    level_report = game.levels[0]
    assert len(level_report.turns) == 2
    assert level_report.turns[0].played_card == 10
    assert level_report.turns[1].played_card == 20
    assert mock_deal.call_count == 2


@patch('themind.game.game.Deck.deal')
def test_game_level_fail_out_of_order(mock_deal: MagicMock):
    """Tests that the game ends if a card is played out of order."""
    # Arrange
    # p2 will play card 20 first because it's a FastAgent (wait time 1)
    # This is incorrect because p1 has a lower card (10)
    players = [DummyAgent(name="p1"), FastAgent(name="p2")]
    game = Game(players)
    game.current_level_number = 1

    # Mock the hands dealt to players
    mock_deal.side_effect = [[10], [20]]

    # Act
    game.play_level()

    # Assert
    assert game.game_over
    assert len(game.levels) == 1
    level_report = game.levels[0]
    assert len(level_report.turns) == 1
    turn = level_report.turns[0]
    assert turn.played_card == 20
    assert turn.player_who_played == "p2"


@patch('themind.game.game.Deck.deal')
def test_game_review(mock_deal: MagicMock):
    """Tests the game review functionality."""
    # Arrange
    players = [DummyAgent(name="p1"), DummyAgent(name="p2")]
    game = Game(players)
    game.current_level_number = 1
    mock_deal.side_effect = [[15], [25]]

    # Act
    game.play_level()

    # Assert
    assert not game.game_over

    with patch('logging.info') as mock_logging:
        game.print_game_review("p2", game_number=1)
        
        # Get the actual output from the mock
        actual_output = mock_logging.call_args[0][0]

        # Assert that the expected strings are in the actual output
        assert "Game 1:" in actual_output
        assert "\n--- Level 1 ---" in actual_output
        assert "\nTurn 1:" in actual_output
        assert "  Last Card Played: 0" in actual_output
        assert "  Total Cards Remaining on Table: 2" in actual_output
        assert "  Action Taken:" in actual_output
        assert "    p1 played card 15 after waiting 10s." in actual_output
        assert "  Your Recommendation:" in actual_output
        assert "    You wanted to play card 25 and wait 10s." in actual_output
