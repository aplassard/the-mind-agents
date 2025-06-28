import logging
from typing import Optional

from .agents import Agent, AgentResponse
from dotenv import load_dotenv
from llmutils.llm_with_retry import call_llm_with_retry
from llmutils.self_healing import heal_llm_output

load_dotenv()


PROMPT = """
You are playing "The Mind"
Objective:
As a team, play cards from 1-100 into a central pile in perfect ascending order. Successfully play all cards from all players' hands to pass a level. The number of cards per player increases with each level.

Core Mechanics:

- Ascending Order is Law: Cards must be played in strictly increasing value. Playing a card while another player holds a lower one results in a mistake.
- No Communication: All forms of explicit signaling (gestures, talk, etc.) about your hand are forbidden.
- Play by Feel (Timing): The decision to play is based on a shared, unspoken sense of timing. The smaller the numeric gap between the last card played and your lowest card, the faster you should play it. Always focus on playing your lowest card first.

Key Events:

- Mistake: Ends the game
- Level Cleared: When all cards have been legally played, the team advances to the next level. 

The current state of the game is 
{game_state}

How many seconds do you want to wait before playing your next card? Your response should be an integer number of seconds

Your current strategy notes are
{notes}

Your response should be in the format
seconds: <number of seconds>
"""

game_state_prompt = """
The most recent card played was {last_played_card}
You have {hand} in your hand and your next card to be played is {next_card}
There are {num_other_cards} cards remaining around the table
"""


def create_game_state(
    hand: list[int], last_played_card: int, num_other_cards: int
) -> str:
    """Creates a string describing the current game state for the LLM.

    Args:
        hand: The agent's current hand.
        last_played_card: The last card played on the pile.
        num_other_cards: The total number of cards in other players' hands.

    Returns:
        A formatted string describing the game state.
    """
    return game_state_prompt.format(
        last_played_card=last_played_card,
        hand=hand,
        next_card=min(hand),
        num_other_cards=num_other_cards,
    )


def parse_message(message: str) -> Optional[int]:
    """Parses the LLM's response to extract the number of seconds to wait.

    Args:
        message: The message from the LLM.

    Returns:
        The number of seconds to wait, or None if it could not be parsed.
    """
    lines = message.splitlines()
    seconds = None
    for line in lines:
        if line.startswith("seconds:"):
            parts = line.split(":", 1)
            if len(parts) > 1:
                if parts[1].strip().isdigit():
                    seconds = int(parts[1])
    return seconds


class LLMAgent(Agent):
    """An agent that uses a large language model to decide how long to wait."""

    def __init__(
        self,
        name: str,
        model_name: str = "openai/gpt-4.1-mini",
    ):
        """Initializes the LLMAgent.

        Args:
            name: The name of the agent.
            model_name: The name of the language model to use.
        """
        super().__init__(name)
        self.model = model_name
        logging.info(f"LLMAgent '{self.name}' initialized with model '{self.model}'.")

    def decide_move(
        self, last_played_card: int, num_other_cards: int
    ) -> AgentResponse:
        """Uses an LLM to decide the best move.

        The method creates a game state prompt, calls the LLM, and parses the
        response. If the response is not in the expected format, it uses a
        self-healing mechanism to attempt to fix it.

        Args:
            last_played_card: The last card played on the pile.
            num_other_cards: The total number of cards in other players' hands.

        Returns:
            An AgentResponse with the card to play and the time to wait.
        """
        game_state = create_game_state(self.hand, last_played_card, num_other_cards)
        message = PROMPT.format(game_state=game_state, notes=self.notes)
        
        logging.debug(f"Agent '{self.name}' sending prompt to LLM: {message}")
        response = call_llm_with_retry(self.model, message)
        logging.debug(f"Agent '{self.name}' received response from LLM: {response}")

        time_to_wait = parse_message(response)

        if time_to_wait is None:
            logging.warning(f"Agent '{self.name}' could not parse LLM response. Attempting to heal.")
            parsing_code = '''
def parse_message(message):
    lines = message.splitlines()
    seconds = None
    for line in lines:
        if line.startswith("seconds:"):
            parts = line.split(":", 1)
            if len(parts) > 1:
                if parts[1].strip().isdigit():
                    seconds = int(parts[1])
    return seconds
'''
            healed_response = heal_llm_output(
                broken_text=response,
                expected_format="seconds: <integer>",
                instructions="Your task is to correct the provided text to match the specified format. Analyze the examples to understand the desired output. The text should only contain the corrected text that can be parsed by the parsing code.",
                good_examples=["seconds: 10", "seconds: 5"],
                bad_examples=["I think I will wait 5 seconds.", "10"],
                parsing_code=parsing_code,
                model_name=self.model,
            )
            logging.debug(f"Agent '{self.name}' received healed response: {healed_response}")
            time_to_wait = parse_message(healed_response)
            if time_to_wait is None:
                logging.error(f"Agent '{self.name}' failed to heal LLM response. Falling back to default wait time.")
                time_to_wait = 10  # Fallback

        card_to_play = min(self.hand)
        logging.info(f"Agent '{self.name}' decided to play card {card_to_play} and wait {time_to_wait} seconds.")
        return AgentResponse(card_to_play=card_to_play, time_to_wait=time_to_wait)

    def review_game(self, game_reviews: list[str]):
        """Reviews the game history and updates the agent's notes."""
        history_string = "\n\n".join(game_reviews)
        logging.debug(f"Agent '{self.name}' reviewing game history: {history_string}")

        prompt = f"""You are an expert player at the game The Mind. You have just completed a series of games and are reviewing your performance to improve your strategy. Below is the game history from your perspective and your current notes.

Game History:
{history_string}

Your Current Strategy Notes:
{self.notes}

Based on the game history, please analyze your performance and provide an updated, concise strategy to improve your play in the next game. Your notes should be a list of rules or heuristics. Your response should only be the updated notes.
"""
        logging.debug(f"Agent '{self.name}' sending review prompt to LLM: {prompt}")
        response = call_llm_with_retry(self.model, prompt)
        logging.debug(f"Agent '{self.name}' received updated notes from LLM: {response}")
        self.notes = response
        logging.info(f"Agent '{self.name}' updated its notes.")

