import pytest
from unittest.mock import patch
from themind.agents.llmagent import LLMAgent, parse_message
from themind.agents.agents import AgentResponse

def test_parse_message():
    """Tests that the message parser correctly extracts the wait time."""
    message = "Some text before\nseconds: 15\nSome text after"
    assert parse_message(message) == 15

def test_parse_message_no_seconds():
    """Tests that the message parser returns None when no wait time is found."""
    message = "Some text without the magic word."
    assert parse_message(message) is None

def test_parse_message_invalid_format():
    """Tests that the message parser returns None for malformed input."""
    message = "seconds: fifteen"
    assert parse_message(message) is None

@patch('themind.agents.llmagent.call_llm_with_retry')
def test_llmagent_decide_move_unit(mock_call_llm):
    """
    Unit test for LLMAgent.decide_move.
    Mocks the LLM call to isolate the agent's logic.
    """
    # Arrange
    mock_call_llm.return_value = "seconds: 12"
    agent = LLMAgent(name="test_agent")
    agent.receive_hand([10, 25, 60])

    # Act
    response = agent.decide_move(last_played_card=5, num_other_cards=3)

    # Assert
    assert isinstance(response, AgentResponse)
    assert response.card_to_play == 10
    assert response.time_to_wait == 12
    mock_call_llm.assert_called_once()

@patch('themind.agents.llmagent.heal_llm_output')
@patch('themind.agents.llmagent.call_llm_with_retry')
def test_llmagent_decide_move_with_healing(mock_call_llm, mock_heal_llm):
    """
    Tests that the self-healing mechanism is triggered when the LLM
    returns a malformed response.
    """
    # Arrange
    mock_call_llm.return_value = "I think I will wait 5 seconds."
    mock_heal_llm.return_value = "seconds: 5"
    agent = LLMAgent(name="test_agent")
    agent.receive_hand([10, 25, 60])

    # Act
    response = agent.decide_move(last_played_card=5, num_other_cards=3)

    # Assert
    assert isinstance(response, AgentResponse)
    assert response.card_to_play == 10
    assert response.time_to_wait == 5
    mock_call_llm.assert_called_once()
    mock_heal_llm.assert_called_once()


@pytest.mark.integration
def test_llmagent_decide_move_integration():
    """
    Integration test for LLMAgent.decide_move.
    This test makes a real call to the LLM.
    It requires a valid OPENROUTER_API_KEY to be set in the environment.
    """
    # Arrange
    agent = LLMAgent(name="integration_test_agent")
    agent.receive_hand([30, 70])

    # Act
    response = agent.decide_move(last_played_card=20, num_other_cards=5)

    # Assert
    assert isinstance(response, AgentResponse)
    assert response.card_to_play == 30
    assert isinstance(response.time_to_wait, int)
    assert response.time_to_wait is not None

