import os
import json
from .game import Game, Turn


class GameResultRepository:
    """Handles saving and loading of game results."""

    def __init__(self, results_dir: str):
        self.results_dir = results_dir
        os.makedirs(self.results_dir, exist_ok=True)

    def save_game_results(self, game: Game, game_number: int, team_guid: str):
        """Saves the results of a single game to disk."""
        game_dir = os.path.join(self.results_dir, team_guid, str(game_number))
        os.makedirs(game_dir, exist_ok=True)

        for level in game.levels:
            level_data = []
            for turn in level.turns:
                turn_data = self._format_turn_data(turn)
                level_data.append(turn_data)

            level_file_path = os.path.join(game_dir, f"{level.level_number}.json")
            with open(level_file_path, 'w') as f:
                json.dump(level_data, f, indent=4)

    def get_game_history(self, game_number: int, team_guid: str) -> dict:
        """Retrieves the history of a single game from disk."""
        game_dir = os.path.join(self.results_dir, team_guid, str(game_number))
        game_history = {}
        for level_file in os.listdir(game_dir):
            level_number = int(level_file.split('.')[0])
            with open(os.path.join(game_dir, level_file), 'r') as f:
                game_history[level_number] = json.load(f)
        return game_history

    def _format_turn_data(self, turn: Turn) -> dict:
        """Formats the turn data into the desired dictionary structure."""
        turn_data = {
            "Previous-card": turn.last_played_card,
            "Acting-player": turn.player_who_played,
            "Card played": turn.played_card,
            "Seconds waited": turn.recommended_actions[turn.player_who_played].time_to_wait,
            "Correct decision": turn.correct_decision,
        }

        for player_name, hand in turn.player_hands.items():
            turn_data[f"{player_name}-hand"] = sorted(hand)
            if hand:
                lowest_card = min(hand)
                turn_data[f"{player_name}-lowest-card"] = lowest_card
                if player_name in turn.recommended_actions:
                    turn_data[f"{player_name}-seconds"] = turn.recommended_actions[player_name].time_to_wait
                else:
                    turn_data[f"{player_name}-seconds"] = None
            else:
                turn_data[f"{player_name}-lowest-card"] = None
                turn_data[f"{player_name}-seconds"] = None

        return turn_data
