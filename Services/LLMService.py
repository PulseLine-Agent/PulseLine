import asyncio
import json

from groq import Groq

from typing import List

from Chat.chat import ChatSession, Message

from Configs.config import GROQ_API_KEY, LLM_CONFIG

from Services.ToolCalls import get_patient_info, set_next_visit, refill_prescription

class LLMService:
    def __init__(self, MODEL) -> None:
        self.client = Groq(api_key=GROQ_API_KEY)
        self.MODEL = MODEL
    
    # Converts a list of messages into a standardized list of dictionaries,
    # ensuring each message has 'role' and 'content' keys regardless of whether
    # the input messages are dicts or objects with attributes.
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
    
    # This async function sends a request to a language model API (Groq) to generate a chat response.
    # It handles message conversion, sending the request with function tool calls,
    # processes any function calls returned by the model, executes those functions asynchronously,
    # and sends a follow-up request if needed to continue the conversation.
    async def generate_response(self, chat_sessions: ChatSession, session_id):
        try:
            print("Preparing LLM request")
            
            converted = self._convert_to_dict(chat_sessions[session_id].messages)
            
            print(f"Sending request to Groq API with {len(chat_sessions[session_id].messages)} messages")
            
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.MODEL,
                messages=converted,
                temperature=LLM_CONFIG["temperature"],
                max_tokens=LLM_CONFIG["max_tokens"],
                top_p=LLM_CONFIG["top_p"],
                stop=LLM_CONFIG["stop"],
                stream=False,
                tools=[
                    {
                        "type": "function",
                        "function": {
                            "name": "get_patient_info",
                            "description": "Fetch patient details by their first and last name.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "first_name": {
                                        "type": "string",
                                        "description": "First name of the patient"
                                    },
                                    "last_name": {
                                        "type": "string",
                                        "description": "Last name of the patient"
                                    }
                                },
                                "required": ["first_name", "last_name"]
                            }
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "set_next_visit",
                            "description": "Sets a patient’s next appointment date.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "first_name": {
                                        "type": "string",
                                        "description": "First name of the patient"
                                    },
                                    "last_name": {
                                        "type": "string",
                                        "description": "Last name of the patient"
                                    },
                                    "next_visit": {
                                        "type": "string",
                                        "description": "The next visit date (YYYY-MM-DD)"
                                    }
                                },
                                "required": ["first_name", "last_name", "next_visit"]
                            }
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "refill_prescription",
                            "description": "Refills patient prescription.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "first_name": {
                                        "type": "string",
                                        "description": "First name of the patient"
                                    },
                                    "last_name": {
                                        "type": "string",
                                        "description": "Last name of the patient"
                                    }
                                },
                                "required": ["first_name", "last_name"]
                            }
                        }
                    }
                ]
            )
            
            if response.choices[0].message.tool_calls:
                tc = response.choices[0].message.tool_calls[0]
                args = json.loads(tc.function.arguments)
                
                if tc.function.name == "get_patient_info":
                    result = await get_patient_info(args["first_name"], args["last_name"])
                elif tc.function.name == "refill_prescription":
                    result = await refill_prescription(args["first_name"], args["last_name"])
                else:
                    result = await set_next_visit(args["first_name"], args["last_name"], args['next_visit'])
                
                chat_sessions[session_id].messages.append(Message(role='system', content=f"This is the result of your tool call: {result}"))
                
                converted_followup = self._convert_to_dict(chat_sessions[session_id].messages)
                
                followup = await asyncio.to_thread(
                    self.client.chat.completions.create,
                    model=self.MODEL,
                    messages=converted_followup,
                    temperature=LLM_CONFIG["temperature"],
                    max_tokens=LLM_CONFIG["max_tokens"],
                    top_p=LLM_CONFIG["top_p"],
                    stop=LLM_CONFIG["stop"],
                    stream=False
                )
                
                print("Finished streaming response")
                return followup
            
            print("Finished streaming response")
            return response
            
        except Exception as e:
            print(f"Error in LLM service: {e}")
            return "I'm sorry, I encountered an error processing your request."