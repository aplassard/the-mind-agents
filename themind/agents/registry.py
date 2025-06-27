from .agents import RandomAgent, PerfectAgent, NoisyAgent, DummyAgent, FastAgent
from .llmagent import LLMAgent

AGENT_REGISTRY = {
    "RandomAgent": RandomAgent,
    "PerfectAgent": PerfectAgent,
    "NoisyAgent": NoisyAgent,
    "DummyAgent": DummyAgent,
    "FastAgent": FastAgent,
    "LLMAgent": LLMAgent,
}
