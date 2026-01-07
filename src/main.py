import argparse
import os
from dotenv import load_dotenv
from openai import OpenAI


def main():
    parser = argparse.ArgumentParser(
        description="Query OpenAI API with a custom prompt"
    )
    parser.add_argument(
        "--query",
        type=str,
        default=(
            """What are often overlooked tips for AI engineering?
            Use one paragraph maximum."""
        ),
        help="The query/prompt to send to OpenAI API"
    )
    args = parser.parse_args()

    load_dotenv()

    api_key = os.environ.get("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)

    prompt = args.query
    messages = [
        {
            "role": "user",
            "content": prompt
        }
    ]

    model = os.environ.get("OPENAI_MODEL")
    response = client.chat.completions.create(
        model=model,
        messages=messages
    )

    print(response.choices[0].message.content)

    if response is None or response.usage is None:
        return
    print(f"Prompt tokens: {response.usage.prompt_tokens}")
    print(f"Response tokens: {response.usage.completion_tokens}")


if __name__ == "__main__":
    main()
