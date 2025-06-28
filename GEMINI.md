# Gemini Development Environment Guide

This document provides instructions for an AI assistant on how to work with the code in this repository.

## Running the Game with a Configuration File

To run the game with a specific configuration, use the following command:

```bash
uv run python -m themind.main <path_to_config_file>
```

For example, to run the game with the `example_game.yaml` configuration, you would use:

```bash
uv run python -m themind.main ./configs/example_game.yaml
```

This will start the game with the agents and settings specified in the configuration file.

## Running Individual Files

To execute a specific Python script within the project's environment, use the `uv run` command. This ensures that the script runs with the correct dependencies from the virtual environment.

**Example:**

```bash
uv run python ./themind/game/game.py
```

## Running the Test Suite

This project uses `pytest` for testing. To execute the full test suite, use the following command:

```bash
uv run pytest
```

To run the tests without the integration tests, use the following command:

```bash
uv run pytest -m "not integration"
```

### When to Run Tests

**Always run the test suite after making any modifications to the code.** This is a critical step to verify that your changes have not introduced any regressions or broken existing functionality. Before committing any changes, ensure that all tests are passing.
