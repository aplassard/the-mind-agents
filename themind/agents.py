from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class AgentResponse:
    """The response from an agent for a given turn."""
    card_to_play: int
    time_to_wait: int


class Agent(ABC):
    """Abstract base class for a player in The Mind."""

    def __init__(self, name: str):
        self.name = name
        self.hand: list[int] = []

    def receive_hand(self, hand: list[int]):
        """Receives a new hand of cards for the next level."""
        self.hand = sorted(hand)

    @abstractmethod
    def decide_move(self, last_played_card: int, num_other_cards: int) -> AgentResponse:
        """
        The core logic of the agent. Decides which card to play and how long to wait.

        Args:
            last_played_card: The card most recently played on the pile.
            num_other_cards: The total number of cards in other players' hands.

        Returns:
            An AgentResponse containing the card to play and the time to wait.
        """
        pass
