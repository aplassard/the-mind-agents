# The Mind - Agents

This project implements a simulation of the card game "The Mind" where players are controlled by AI agents.

## Overview

The game is designed to be played by autonomous agents that inherit from the `themind.agents.Agent` class. The core logic of the game is implemented in `themind.game.py`, and the agents' decision-making processes are defined in `themind.agents.py`.

## Getting Started

### Prerequisites

- Python 3.12+
- `uv` package manager

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/the-mind-agents.git
    cd the-mind-agents
    ```

2.  **Install dependencies using `uv`:**

    `uv` will create a virtual environment and install the required packages from `pyproject.toml`.

    ```bash
    uv pip install -e .
    ```

## How to Use

### Running the Game

To run the game, you will need to create a script that imports the `Game` class and the agent implementations you want to use. Here is a basic example:

```python
# run_game.py
from themind.game import Game
from themind.agents import YourAgentImplementation # Replace with your agent

if __name__ == "__main__":
    players = [
        YourAgentImplementation(name="Agent 1"),
        YourAgentImplementation(name="Agent 2"),
    ]

    game = Game(players)
    game.play()

    # Review the game from a player's perspective
    game.review_game("Agent 1")
```

### Running Tests

To run the test suite, use the following command:

```bash
uv run pytest
```

This will execute the tests located in the `tests/` directory.

## Project Structure

```
.the-mind-agents/
├── themind/
│   ├── __init__.py
│   ├── agents.py     # Agent base class and implementations
│   └── game.py       # Core game logic (Game, Deck, Level, Turn)
├── tests/
│   └── test_game.py  # Pytests for the game logic
├── .gitignore
├── pyproject.toml    # Project metadata and dependencies
└── README.md
```

## Game Rules

This implementation follows a simplified version of "The Mind":

-   **Objective:** Play cards in ascending order without communication.
-   **Losing:** The game ends immediately if a card is played out of order (i.e., a player plays a card when another player holds a lower one).
-   **No Lives/Shurikens:** This version does not include lives or throwing stars.
-   **Continuous Play:** The game continues until a mistake is made.