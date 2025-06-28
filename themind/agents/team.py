import uuid
import os
import json
import logging
from ..game import Game
from .agents import Agent


class Team:
    """Manages a team of agents playing multiple games of The Mind."""

    def __init__(self, agents: list[Agent], num_games: int, results_dir: str = "./results"):
        self.agents = agents
        self.num_games = num_games
        self.team_guid = str(uuid.uuid4())
        self.results_dir = os.path.join(results_dir, self.team_guid)
        self.agent_review_histories: dict[str, list[str]] = {}
        os.makedirs(self.results_dir, exist_ok=True)
        logging.info(f"Team {self.team_guid} created. Results will be saved to {self.results_dir}")

    def play_games(self):
        """Plays the specified number of games."""
        for i in range(self.num_games):
            game_number = i + 1
            logging.info(f"\n--- Starting Game {game_number} for Team {self.team_guid} ---")
            game = Game(self.agents)
            game.play()

            # Save game results
            self.save_game_results(game, game_number)

            # Print game review for user
            logging.info("\n--- Game Review ---")
            for agent in self.agents:
                game.print_game_review(agent.name, game_number)

            # Agents learn from the game
            logging.info("\n--- Agents Learning ---")
            for agent in self.agents:
                # Generate the review text from the agent's perspective
                review_text = game._generate_game_review_text(agent.name, game_number)
                
                # Append the new review to the agent's history
                history = self.agent_review_histories.setdefault(agent.name, [])
                history.append(review_text)

                # Pass the full history of text-based reviews to the agent
                agent.review_game(history)

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

    def get_game_history(self, game_number: int) -> dict:
        """Retrieves the history of a single game from disk."""
        game_dir = os.path.join(self.results_dir, str(game_number))
        game_history = {}
        for level_file in os.listdir(game_dir):
            level_number = int(level_file.split('.')[0])
            with open(os.path.join(game_dir, level_file), 'r') as f:
                game_history[level_number] = json.load(f)
        return game_history

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
