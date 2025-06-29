import argparse
import yaml
import logging
from .agents import AGENT_REGISTRY
from .agents.team import Team
from .game import Game

def main():
    parser = argparse.ArgumentParser(description="Run The Mind game with a specified configuration.")
    parser.add_argument("config_file", help="Path to the YAML configuration file.")
    args = parser.parse_args()

    with open(args.config_file, 'r') as f:
        config = yaml.safe_load(f)

    log_level_str = config.get("log_level", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')

    game_name = config.get("game_name", "The Mind Game")
    agents_config = config.get("agents", [])
    num_games = config.get("num_games", 1)
    results_dir = config.get("results_dir", "./results")

    agents = []
    for agent_conf in agents_config:
        agent_type = agent_conf.get("type")
        agent_name = agent_conf.get("name", agent_type)
        agent_params = agent_conf.get("params", {})

        if agent_type in AGENT_REGISTRY:
            agent_class = AGENT_REGISTRY[agent_type]
            agents.append(agent_class(name=agent_name, **agent_params))
        else:
            logging.error(f"Unknown agent type: {agent_type}")
            raise ValueError(f"Unknown agent type: {agent_type}")

    logging.info(f"Starting game: {game_name}")
    team = Team(agents, num_games, results_dir)
    team.play_games()

if __name__ == "__main__":
    main()
