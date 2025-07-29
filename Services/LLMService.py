import asyncio
from groq import Groq

from agno.agent import Agent

from typing import AsyncGenerator

from Configs.config import GROQ_API_KEY, LLM_CONFIG
from Configs.prompts import CALL_PROMPT


class LLMService:
    def __init__(self) -> None:
        self.client = Groq(api_key=GROQ_API_KEY)

    async def generate_response_stream(
        self, messages, model_name: str, reason: bool, tools=[]
    ) -> AsyncGenerator[str, None]:
        try:
            print("Preparing LLM request")

            start_message = {"role": "system", "content": CALL_PROMPT}

            messages.insert(0, start_message)

            print(f"Sending request to Groq API with {len(messages)} messages")

            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=model_name,
                messages=messages,
                temperature=LLM_CONFIG["temperature"],
                max_tokens=LLM_CONFIG["max_tokens"],
                top_p=LLM_CONFIG["top_p"],
                stream=True,
                stop=LLM_CONFIG["stop"],
            )

            print("Got streaming response from Groq API")

            # Stream the chunks back
            for chunk in response:
                content = chunk.choices[0].delta.content
                if content:
                    yield content

            print("Finished streaming response")

        except Exception as e:
            print(f"Error in LLM service: {e}")
            yield "I'm sorry, I encountered an error processing your request."
