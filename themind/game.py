import random
from dataclasses import dataclass, field
from themind.agents import Agent, AgentResponse


@dataclass
class Turn:
    """Represents a single turn within a level."""
    last_played_card: int
    player_hands: dict[str, list[int]]
    recommended_actions: dict[str, AgentResponse]
    played_card: int
    player_who_played: str


@dataclass
class Level:
    """Represents a single level of the game."""
    level_number: int
    turns: list[Turn] = field(default_factory=list)


class Deck:
    """Represents the deck of cards."""

    def __init__(self):
        self.cards = list(range(1, 101))
        self.shuffle()

    def shuffle(self):
        """Shuffles the deck."""
        random.shuffle(self.cards)

    def deal(self, num_cards: int) -> list[int]:
        """Deals a hand of cards."""
        return [self.cards.pop() for _ in range(num_cards)]


class Game:
    """Manages the game of The Mind."""

    def __init__(self, players: list[Agent]):
        self.players = players
        self.deck = Deck()
        self.levels: list[Level] = []
        self.current_level_number = 1
        self.game_over = False

    def play(self):
        """Starts and runs the game until it's over."""
        while not self.game_over:
            self.play_level()

    def play_level(self):
        """Plays a single level of the game."""
        level = Level(level_number=self.current_level_number)
        self.levels.append(level)
        self.deck = Deck()

        cards_to_deal = self.current_level_number * len(self.players)
        if cards_to_deal > 100: # A new deck has 100 cards
            print(f"Game Over! Not enough cards in a new deck to deal for level {self.current_level_number}.")
            self.game_over = True
            return

        for player in self.players:
            hand = self.deck.deal(self.current_level_number)
            player.receive_hand(hand)

        last_played_card = 0
        cards_in_play = self.current_level_number * len(self.players)

        while cards_in_play > 0:
            recommended_actions: dict[str, AgentResponse] = {}
            for player in self.players:
                if player.hand:
                    num_other_cards = sum(len(p.hand) for p in self.players if p != player)
                    recommended_actions[player.name] = player.decide_move(
                        last_played_card, num_other_cards
                    )

            if not recommended_actions:
                break

            player_who_played_name = min(
                recommended_actions,
                key=lambda p: recommended_actions[p].time_to_wait
            )

            action = recommended_actions[player_who_played_name]
            played_card = action.card_to_play

            player_who_played = next(
                p for p in self.players if p.name == player_who_played_name
            )

            turn = Turn(
                last_played_card=last_played_card,
                player_hands={p.name: p.hand.copy() for p in self.players},
                recommended_actions=recommended_actions,
                played_card=played_card,
                player_who_played=player_who_played.name,
            )
            level.turns.append(turn)

            all_remaining_cards = []
            for p in self.players:
                all_remaining_cards.extend(p.hand)

            if played_card != min(all_remaining_cards):
                correct_card = min(all_remaining_cards)
                owner_of_correct_card = "unknown"
                for p in self.players:
                    if correct_card in p.hand:
                        owner_of_correct_card = p.name
                        break
                print(
                    f"Game Over! Card {played_card} was played by {player_who_played.name}, "
                    f"but {owner_of_correct_card} had a lower card ({correct_card})."
                )
                self.game_over = True
                return

            last_played_card = played_card
            player_who_played.hand.remove(played_card)
            cards_in_play -= 1

        self.current_level_number += 1

    def review_game(self, player_name: str):
        """Allows a player to review the game from their perspective."""
        for level in self.levels:
            print(f"\n--- Level {level.level_number} ---")
            for i, turn in enumerate(level.turns):
                print(f"\nTurn {i + 1}:")
                print(f"  Last Card Played: {turn.last_played_card}")
                total_cards_remaining = sum(len(hand) for hand in turn.player_hands.values())
                print(f"  Total Cards Remaining on Table: {total_cards_remaining}")

                time_waited = turn.recommended_actions[turn.player_who_played].time_to_wait
                print("  Action Taken:")
                print(f"    {turn.player_who_played} played card {turn.played_card} after waiting {time_waited}s.")

                if player_name in turn.recommended_actions and turn.player_who_played != player_name:
                    player_action = turn.recommended_actions[player_name]
                    print("  Your Recommendation:")
                    print(
                        f"    You wanted to play card {player_action.card_to_play} "
                        f"and wait {player_action.time_to_wait}s."
                    )
