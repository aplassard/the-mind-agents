import uuid
import os
import json
from ..game import Game
from .agents import Agent


class Team:
    """Manages a team of agents playing multiple games of The Mind."""

    def __init__(self, agents: list[Agent], num_games: int, results_dir: str = "./results"):
        self.agents = agents
        self.num_games = num_games
        self.team_guid = str(uuid.uuid4())
        self.results_dir = os.path.join(results_dir, self.team_guid)
        os.makedirs(self.results_dir, exist_ok=True)

    def play_games(self):
        """Plays the specified number of games."""
        for i in range(self.num_games):
            game_number = i + 1
            print(f"\n--- Starting Game {game_number} for Team {self.team_guid} ---")
            game = Game(self.agents)
            game.play()

            # Save game results
            self.save_game_results(game, game_number)

            # Review game
            print("\n--- Reviewing Game ---")
            for agent in self.agents:
                game.review_game(agent.name)

    def save_game_results(self, game: Game, game_number: int):
        """Saves the results of a single game to disk."""
        game_dir = os.path.join(self.results_dir, str(game_number))
        os.makedirs(game_dir, exist_ok=True)

        for level in game.levels:
            level_data = []
            for turn in level.turns:
                turn_data = self._format_turn_data(turn)
                level_data.append(turn_data)

            level_file_path = os.path.join(game_dir, f"{level.level_number}.json")
            with open(level_file_path, 'w') as f:
                json.dump(level_data, f, indent=4)

    def _format_turn_data(self, turn) -> dict:
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
