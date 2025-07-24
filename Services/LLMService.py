from agno.agent import Agent
from agno.models.groq import Groq

from Configs.config import CALL_PROMPT

from dotenv import load_dotenv

load_dotenv()

class LLMService:
    def __init__(self) -> None:
        self.model = Agent(
            model=Groq(id='llama-3.3-70b-versatile'),
            instructions=CALL_PROMPT,            
            show_tool_calls=True,
            )