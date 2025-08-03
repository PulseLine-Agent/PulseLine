import asyncio
from groq import Groq

from typing import AsyncGenerator, List

from Chat.chat import Message

from Configs.config import GROQ_API_KEY, LLM_CONFIG
from Configs.prompts import CALL_PROMPT, ONLINE_PROMPT

# TODO Give tool choices to LLM

class LLMService:
    def __init__(self) -> None:
        self.client = Groq(api_key=GROQ_API_KEY)
        
    def _convert_to_dict(self, messages: List[Message]):
        converted = []
        for msg in messages:
            if isinstance(msg, dict):
                converted.append({
                    "role": msg["role"], 
                    "content": msg["content"]
                })
            else:
                converted.append({
                    "role": msg.role, 
                    "content": msg.content
                })
        return converted

# TODO: Add reason to the prompt + check if qwen3 works because we can't choose when model reasons or not
# TODO: Try adding Qwen3 reasoning as a tool call?

    async def generate_response_stream(
        self, messages, online: bool, tools=[]
    ) -> AsyncGenerator[str, None]:
        try:
            print("Preparing LLM request")
            
            if online:
                start_message = {
                    "role": "system",
                    "content": ONLINE_PROMPT
                }
            else:
                start_message = {
                    "role": "system",
                    "content": CALL_PROMPT
                }

            messages.insert(0, start_message)
            
            converted = self._convert_to_dict(messages)

            print(f"Sending request to Groq API with {len(messages)} messages")
            
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model='llama-3.3-70b-versatile',
                messages=converted,
                temperature=LLM_CONFIG["temperature"],
                max_tokens=LLM_CONFIG["max_tokens"],
                top_p=LLM_CONFIG["top_p"],
                stop=LLM_CONFIG["stop"],
                stream=True
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
