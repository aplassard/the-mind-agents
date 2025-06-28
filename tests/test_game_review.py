
import pytest
from themind.game.game import Game, Level, Turn
from themind.agents.agents import DummyAgent, AgentResponse


def test_review_game_with_empty_hand():
    """
    Tests that review_game handles cases where a player has an empty hand
    and no recommended_actions.
    """
    # Create a game with two dummy agents
    player1 = DummyAgent(name="Player 1")
    player2 = DummyAgent(name="Player 2")
    game = Game(players=[player1, player2])

    # Manually construct a level and turn for the test case
    level = Level(level_number=1)
    turn = Turn(
        last_played_card=0,
        player_hands={"Player 1": [], "Player 2": [10]},  # Player 1 has an empty hand
        recommended_actions={
            "Player 2": AgentResponse(card_to_play=10, time_to_wait=10)
        },
        played_card=10,
        player_who_played="Player 2",
        correct_decision=True,
    )
    level.turns.append(turn)
    game.levels.append(level)

    # Player 1, who has an empty hand, reviews the game.
    # This should not raise a KeyError.
    try:
        game.review_game("Player 1")
    except KeyError:
        pytest.fail("review_game raised a KeyError when a player has an empty hand.")

    # Test that the player's hand is printed correctly
    import io
    from contextlib import redirect_stdout

    f = io.StringIO()
    with redirect_stdout(f):
        game.review_game("Player 1")
    output = f.getvalue()

    assert "Your Hand: []" in output
