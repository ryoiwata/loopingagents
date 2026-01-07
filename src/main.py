import os
from dotenv import load_dotenv
from openai import OpenAI


def main():
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

    if response is None or response.usage is None:
        return
    print(f"Prompt tokens: {response.usage.prompt_tokens}")
    print(f"Response tokens: {response.usage.completion_tokens}")


if __name__ == "__main__":
    main()
