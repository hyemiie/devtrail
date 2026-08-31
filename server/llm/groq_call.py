import os
import uuid
from groq import Groq
from dotenv import load_dotenv

from server.controller.chat import create_chat, createChat

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_URL")
)
    



async def call_grok_chat(content:str, room_id : uuid.UUID):
    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
        {
            "role": "user",
            "content": content
        }
        ],
        temperature=1,
        max_completion_tokens=2048,
        top_p=1,
        reasoning_effort="medium",
        stream=True,
        stop=None
    )
    chat_details = {
        "room_id": room_id, 
        "sender": "system",
        "content" :""
    }

    for chunk in completion:
        groq_response = chunk.choices[0].delta.content or "", end=""
        chat_details["content"]= groq_response
        print("chat_details", chat_details)
        save_chat =  await create_chat(chat_detail=chat_details)
        print ('groq', groq_response, save_chat)
