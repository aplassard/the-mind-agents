import random
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
        self.notes: str = """No notes yet"""

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

    @abstractmethod
    def review_game(self, game_reviews: list[str]):
        """
        Allows the agent to review a completed game and update its notes.

        Args:
            game_reviews: A list of strings, where each string is a review of a past game from the agent's perspective.
        """
        pass


class RandomAgent(Agent):
    """An agent that plays a random card and waits a random amount of time."""

    def __init__(self, name: str, min_wait: int = 0, max_wait: int = 100):
        super().__init__(name)
        self.min_wait = min_wait
        self.max_wait = max_wait

    def decide_move(self, last_played_card: int, num_other_cards: int) -> AgentResponse:
        card_to_play = min(self.hand)
        time_to_wait = random.randint(self.min_wait, self.max_wait)
        return AgentResponse(card_to_play=card_to_play, time_to_wait=time_to_wait)

    def review_game(self, game_reviews: list[str]):
        pass


class PerfectAgent(Agent):
    """An agent that plays perfectly, waiting exactly the difference between the last played card and its lowest card."""

    def decide_move(self, last_played_card: int, num_other_cards: int) -> AgentResponse:
        card_to_play = min(self.hand)
        time_to_wait = card_to_play - last_played_card
        return AgentResponse(card_to_play=card_to_play, time_to_wait=time_to_wait)

    def review_game(self, game_reviews: list[str]):
        pass


class NoisyAgent(Agent):
    """
    An agent that plays like a PerfectAgent but adds an offset and uniform noise to the wait time.
    """

    def __init__(self, name: str, offset: int = 5, noise: int = 2):
        super().__init__(name)
        if offset < 0 or noise < 0:
            raise ValueError("Offset and noise must be non-negative.")
        self.offset = offset
        self.noise = noise

    def decide_move(self, last_played_card: int, num_other_cards: int) -> AgentResponse:
        card_to_play = min(self.hand)
        perfect_time_to_wait = card_to_play - last_played_card
        
        # Calculate noisy time to wait
        noisy_time_to_wait = perfect_time_to_wait + self.offset
        if self.noise > 0:
            noisy_time_to_wait += random.randint(-self.noise, self.noise)
        
        return AgentResponse(card_to_play=card_to_play, time_to_wait=noisy_time_to_wait)

    def review_game(self, game_reviews: list[str]):
        pass


class DummyAgent(Agent):
    """A simple agent for testing that waits a fixed amount of time."""

    def decide_move(
        self, last_played_card: int, num_other_cards: int
    ) -> AgentResponse:
        """Waits a fixed amount of time (10s) before playing."""
        return AgentResponse(card_to_play=min(self.hand), time_to_wait=10)

    def review_game(self, game_review: list[str]):
        """A dummy method to allow for instantiation of the agent."""
        pass

class FastAgent(Agent):
    """A simple agent for testing that waits a short amount of time."""

    def decide_move(self, last_played_card: int, num_other_cards: int) -> AgentResponse:
        card_to_play = min(self.hand)
        return AgentResponse(card_to_play=card_to_play, time_to_wait=1)

    def review_game(self, game_reviews: list[str]):
        pass
