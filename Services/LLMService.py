from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools import tool
from datetime import datetime
import pandas as pd
from Configs.config import CALL_PROMPT
from agno.tools.duckduckgo import DuckDuckGoTools


from dotenv import load_dotenv

load_dotenv()

df = pd.read_csv("Services/data/ex_schedule.csv")

class LLMService:
    def __init__(self) -> None:
        self.agent = Agent(
            model=Groq(id='llama-3.3-70b-versatile'),
            instructions=CALL_PROMPT,            
            show_tool_calls=True,
            )


callAg = Agent(
    name="CallAgent",
    model=Groq(id="llama-3.3-70b-versatile"),
    instructions=CALL_PROMPT
)

appointmentAg = Agent(
    name="appointmentAg",
    model=Groq(id="llama-3.3-70b-versatile"),
    instructions="Review a csv file with a schedule of appointments. Search through and offer the most recent available day as well as 3 different times. Make sure you state the date and what day of the week it is. Read_csv returns df.to_dict thingy that has the first column for dates and first row for time.",
    tools=[],
    show_tool_calls=True,
    markdown=True
)

#print(read_csv())

appointmentAg.print_response("Gimme an appointment date.", stream=True)