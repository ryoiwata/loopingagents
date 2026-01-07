import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.environ.get("OPENAI_API_KEY")
model = os.environ.get("OPENAI_MODEL")

client = OpenAI(api_key=api_key)

response = client.chat.completions.create(
    model=model,
    messages=[
        {
            "role": "user",
            "content": (
                "What are often overlooked tips for AI engineering? "
                "Use one paragraph maximum."
            )
        }
    ]
)

print(response.choices[0].message.content)
