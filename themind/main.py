import argparse
import yaml
from .game import Game
from .agents import AGENT_REGISTRY

def main():
    parser = argparse.ArgumentParser(description="Run The Mind game with a specified configuration.")
    parser.add_argument("config_file", help="Path to the YAML configuration file.")
    args = parser.parse_args()

    with open(args.config_file, 'r') as f:
        config = yaml.safe_load(f)

    game_name = config.get("game_name", "The Mind Game")
    agents_config = config.get("agents", [])

    agents = []
    for agent_conf in agents_config:
        agent_type = agent_conf.get("type")
        agent_name = agent_conf.get("name", agent_type)
        agent_params = agent_conf.get("params", {})

        if agent_type in AGENT_REGISTRY:
            agent_class = AGENT_REGISTRY[agent_type]
            agents.append(agent_class(name=agent_name, **agent_params))
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")

    print(f"Starting game: {game_name}")
    game = Game(agents)
    game.play()
    game.review_game(agents[0].name) # Review from the perspective of the first agent

if __name__ == "__main__":
    main()
