import logging
from .game import Game


class GameReviewer:
    """Generates reviews of a completed game."""

    def __init__(self, game: Game):
        self.game = game

    def print_game_review(self, player_name: str, game_number: int = None):
        """Prints a review of the game from a player's perspective."""
        review_text = self.generate_game_review_text(player_name, game_number)
        logging.info(review_text)

    def generate_game_review_text(self, player_name: str, game_number: int = None) -> str:
        """Generates the game review text from a player's perspective."""
        review_lines = []
        if game_number:
            review_lines.append(f"Game {game_number}:")

        for level in self.game.levels:
            review_lines.append(f"\n--- Level {level.level_number} ---")
            for i, turn in enumerate(level.turns):
                review_lines.append(f"\nTurn {i + 1}:")
                review_lines.append(f"  Last Card Played: {turn.last_played_card}")
                total_cards_remaining = sum(len(hand) for hand in turn.player_hands.values())
                review_lines.append(f"  Total Cards Remaining on Table: {total_cards_remaining}")

                # Display the hand of the player reviewing the game
                if player_name in turn.player_hands:
                    player_hand = turn.player_hands[player_name]
                    review_lines.append(f"  Your Hand: {player_hand}")

                time_waited = turn.recommended_actions[turn.player_who_played].time_to_wait
                review_lines.append("  Action Taken:")
                review_lines.append(f"    {turn.player_who_played} played card {turn.played_card} after waiting {time_waited}s.")

                if not turn.correct_decision:
                    review_lines.append("  Result: Incorrect move.")
                    review_lines.append(f"    - The correct card to play was {turn.correct_card}, which was held by {turn.owner_of_correct_card}.")
                
                if player_name in turn.recommended_actions and turn.player_who_played != player_name:
                    player_action = turn.recommended_actions[player_name]
                    review_lines.append("  Your Recommendation:")
                    review_lines.append(
                        f"    You wanted to play card {player_action.card_to_play} "
                        f"and wait {player_action.time_to_wait}s."
                    )
            
            # Add level summary
            if level.win:
                review_lines.append(f"\n--- Level {level.level_number} Summary ---")
                review_lines.append("  Result: Level cleared successfully!")
            else:
                review_lines.append(f"\n--- Level {level.level_number} Summary ---")
                review_lines.append("  Result: Level failed.")

        return "\n".join(review_lines)
