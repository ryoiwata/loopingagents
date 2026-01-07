import argparse
import json
import os
from datetime import datetime
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
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed information including prompt and token usage"
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

    response_content = response.choices[0].message.content

    # Create logs directory if it doesn't exist
    logs_dir = "logs"
    os.makedirs(logs_dir, exist_ok=True)

    # Generate dynamic filename with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_filename = f"{timestamp}_session.json"
    log_file = os.path.join(logs_dir, log_filename)

    # Prepare log entry with all required fields
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "model": model,
        "prompt": prompt,
        "response": response_content,
        "usage": {
            "prompt_tokens": (
                response.usage.prompt_tokens
                if response.usage is not None
                else None
            ),
            "completion_tokens": (
                response.usage.completion_tokens
                if response.usage is not None
                else None
            )
        }
    }

    # Write JSON log entry to file
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(log_entry, f, indent=2, ensure_ascii=False)

    # Handle verbose output
    if args.verbose:
        print(f"User prompt: {prompt}")
        if response.usage is not None:
            print(f"Prompt tokens: {response.usage.prompt_tokens}")
            print(f"Response tokens: {response.usage.completion_tokens}")
        else:
            print("Prompt tokens: N/A")
            print("Response tokens: N/A")
        print()
        print(response_content)
    else:
        print(response_content)


if __name__ == "__main__":
    main()
