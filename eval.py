import asyncio
import time

from typing import Dict

from groq import Groq

from Chat.chat import ChatSession, Message

from Configs.prompts import ONLINE_PROMPT

from Services.LLMService import LLMService

client = Groq()

EVALUATION_INPUT = 'Schedule me a appointment on July 10th, 2025'
EXPECTED_OUTPUT = "This is the expected output: I’d be happy to help set up that appointment for July 10, 2025. Could you please provide your name so I can schedule this for you?"

llm_service = LLMService('openai/gpt-oss-20b')

EVAL_PROMPT = "You are an expert judge tasked with comparing the quality of an AI Agent’s output to a user-provided expected output. You must assume the expected_output is correct - even if you personally disagree."

session_id = 'evaluation'

# This async function performs an evaluation of an agent-generated response.
# It first gets a response from an LLM service (based on the evaluation input),
# then sends that response along with expected input and prompt to a second model for evaluation.
# Finally, it prints both the AI-generated output and the evaluation result from the second model.
async def evaluation():
    chat_sessions: Dict[str, ChatSession] = {}
    session_id = 'evaluation'

    chat_sessions[session_id] = ChatSession(id=session_id)

    chat_sessions[session_id].messages.append(Message(role='system', content=ONLINE_PROMPT))
    chat_sessions[session_id].messages.append(Message(role='user', content=EVALUATION_INPUT))
    
    response = await llm_service.generate_response(chat_sessions, session_id)
    
    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": EVAL_PROMPT
            },
            {
                "role": "system",
                "content": EVALUATION_INPUT
            },  
            {
                "role": "user",
                "content": EXPECTED_OUTPUT
            },
            {
                "role": "user",
                "content": f"This is the AI agent's output: {response.choices[0].message.content}"
            }
        ]
    )
    
    print(f"{EXPECTED_OUTPUT}\n\nThis is the AI agent's output: {response.choices[0].message.content}\n\n")
    print(completion.choices[0].message.content)

# This async function measures the average response time of an LLM service.
# It simulates multiple chat sessions in a loop, sends predefined prompts,
# and times how long it takes to receive responses.
# At the end, it calculates and prints the average response time per request.
async def average_response_time(loops):
    start = time.time()
    
    for _ in range(loops):
        chat_sessions: Dict[str, ChatSession] = {}

        chat_sessions[session_id] = ChatSession(id=session_id)

        chat_sessions[session_id].messages.append(Message(role='system', content=ONLINE_PROMPT))
        chat_sessions[session_id].messages.append(Message(role='user', content=EVALUATION_INPUT))
        
        await llm_service.generate_response(chat_sessions, session_id)
        
    end = time.time()
    
    print(f"Average time per response: {(end - start) / loops}")

# if __name__ == "__main__":
#     asyncio.run(evaluation())

# Uncomment this to check average response time (can be limited by API rate limit)
if __name__ == "__main__":
    asyncio.run(average_response_time(10))