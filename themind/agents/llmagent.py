from .agents import Agent, AgentResponse
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)

def call_llm(prompt, model="openai/gpt-4.1-mini"):
    completion = client.chat.completions.create(
        model=model,
        messages=[{
            "role": "user",
            "content": prompt
        }])
    print(completion)
    return completion.choices[0].message.content

PROMPT = """
You are playing "The Mind"
Objective:
As a team, play cards from 1-100 into a central pile in perfect ascending order. Successfully play all cards from all players' hands to pass a level. The number of cards per player increases with each level.

Core Mechanics:

- Ascending Order is Law: Cards must be played in strictly increasing value. Playing a card while another player holds a lower one results in a mistake.
- No Communication: All forms of explicit signaling (gestures, talk, etc.) about your hand are forbidden.
- Play by Feel (Timing): The decision to play is based on a shared, unspoken sense of timing. The smaller the numeric gap between the last card played and your lowest card, the faster you should play it. Always focus on playing your lowest card first.

Key Events:

- Mistake: Ends the game
- Level Cleared: When all cards have been legally played, the team advances to the next level. 

The current state of the game is 
{game_state}

How many seconds do you want to wait before playing your next card? Your response should be an integer number of seconds

Your response should be in the format
seconds: <number of seconds>
"""

game_state_prompt = """
The most recent card played was {last_played_card}
You have {hand} in your hand and your next card to be played is {next_card}
There are {num_other_cards} remaining around the table
"""

def create_game_state(hand, last_played_card, num_other_cards):
    return game_state_prompt.format(
        last_played_card=last_played_card,
        hand=hand,
        next_card=min(hand),
        num_other_cards=num_other_cards
    )

def parse_message(message):
    lines = message.split("\n")
    seconds = None
    for line in lines:
        if line.startswith("seconds:"):
            parts = line.split(":", 1)
            if len(parts) > 1:
                if parts[1].strip().isdigit():
                    seconds = int(parts[1])
    return seconds

class LLMAgent(Agent):
    def __init__(self, name: str):
        super().__init__(name)

    def decide_move(self, last_played_card: int, num_other_cards: int) -> AgentResponse:
        game_state = create_game_state(self.hand, last_played_card, num_other_cards)
        message = PROMPT.format(game_state=game_state)
        response = call_llm(message)
        time_to_wait = parse_message(response)
        card_to_play = min(self.hand)
        print(f"Playing {card_to_play} after {time_to_wait} seconds")
        return AgentResponse(card_to_play=card_to_play, time_to_wait=time_to_wait)
