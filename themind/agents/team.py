import uuid
import os
import logging
from ..game import Game
from ..game.review import GameReviewer
from ..game.repo import GameResultRepository
from .agents import Agent


class Team:
    """Manages a team of agents playing multiple games of The Mind."""

    def __init__(self, agents: list[Agent], num_games: int, results_dir: str = "./results"):
        self.agents = agents
        self.num_games = num_games
        self.team_guid = str(uuid.uuid4())
        self.agent_review_histories: dict[str, list[str]] = {}
        self.games: list[Game] = []
        self.repo = GameResultRepository(results_dir)
        logging.info(f"Team {self.team_guid} created. Results will be saved to {results_dir}")

    def play_games(self):
        """Plays the specified number of games."""
        for i in range(self.num_games):
            game_number = i + 1
            logging.info(f"\n--- Starting Game {game_number} for Team {self.team_guid} ---")
            game = Game(self.agents)
            self.games.append(game)
            game.play()

            # Save game results
            self.repo.save_game_results(game, game_number, self.team_guid)

            # Print game review for user
            logging.info("\n--- Game Review ---")
            reviewer = GameReviewer(game)
            for agent in self.agents:
                reviewer.print_game_review(agent.name, game_number)

            # Agents learn from the game
            logging.info("\n--- Agents Learning ---")
            for agent in self.agents:
                # Generate the review text from the agent's perspective
                review_text = reviewer.generate_game_review_text(agent.name, game_number)
                
                # Append the new review to the agent's history
                history = self.agent_review_histories.setdefault(agent.name, [])
                history.append(review_text)

                # Pass the full history of text-based reviews to the agent
                agent.review_game(history)

        for i, game in enumerate(self.games):
            if not game.is_win():
                game_number = i + 1
                level_lost = game.level_lost
                cards_played = game.cards_played_on_loss
                total_cards = game.total_cards_on_loss
                percent_played = (cards_played / total_cards) * 100 if total_cards > 0 else 0
                logging.info(f"Game {game_number}: Lost on level {level_lost}, "
                             f"cards played: {cards_played}/{total_cards} ({percent_played:.2f}%)")
