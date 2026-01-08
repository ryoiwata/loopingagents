import argparse
import json
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# Add src directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.normpath(os.path.join(current_dir, ".."))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from agent_core.providers.prompt_loader import (  # noqa: E402
    get_active_system_prompt
)


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

    prompt = args.query
    model = os.environ.get("OPENAI_MODEL")

    # Load active system prompt and parameters from YAML
    system_template, parameters = get_active_system_prompt()
    temperature = parameters.get("temperature", 0)

    # Create ChatPromptTemplate from loaded system prompt
    chat_template = ChatPromptTemplate.from_messages([
        ("system", system_template),
        ("human", "{user_input}"),
    ])

    # Initialize LangChain ChatOpenAI model with parameters from YAML
    # Some models don't support temperature=0, so we'll use None (default) if 0
    llm_kwargs = {"model": model}
    if temperature != 0:
        llm_kwargs["temperature"] = temperature
    llm = ChatOpenAI(**llm_kwargs)

    # Format messages using the template
    formatted_messages = chat_template.format_messages(user_input=prompt)

    # Invoke the model
    try:
        response = llm.invoke(formatted_messages)
    except Exception as e:
        # If temperature=0 is not supported, retry with default temperature
        if "temperature" in str(e).lower() and temperature == 0:
            llm = ChatOpenAI(model=model)  # Use default temperature
            response = llm.invoke(formatted_messages)
        else:
            raise

    # Extract content from AIMessage
    response_content = response.content

    # Extract token usage from response metadata
    prompt_tokens = None
    completion_tokens = None
    if hasattr(response, "response_metadata") and response.response_metadata:
        usage = response.response_metadata.get("token_usage", {})
        prompt_tokens = usage.get("prompt_tokens")
        completion_tokens = usage.get("completion_tokens")

    # Create logs directory if it doesn't exist
    logs_dir = "logs"
    os.makedirs(logs_dir, exist_ok=True)

    # Generate timestamped log filename (JSON format)
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"session_{timestamp_str}.json"
    log_file = os.path.join(logs_dir, log_filename)

    # Prepare log entry with all required fields
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "model": model,
        "system_prompt": system_template,
        "prompt": prompt,
        "response": response_content,
        "usage": {
            "prompt_tokens": (
                prompt_tokens if prompt_tokens is not None else None
            ),
            "completion_tokens": (
                completion_tokens if completion_tokens is not None else None
            )
        }
    }

    # Write pretty-printed JSON log entry to file
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(log_entry, f, indent=4, ensure_ascii=False)

    # Handle verbose output
    if args.verbose:
        # Show truncated system prompt
        system_preview = (
            system_template[:100] + "..."
            if len(system_template) > 100
            else system_template
        )
        print(f"System Prompt (truncated): {system_preview}")
        print(f"User prompt: {prompt}")
        if prompt_tokens is not None and completion_tokens is not None:
            print(f"Prompt tokens: {prompt_tokens}")
            print(f"Response tokens: {completion_tokens}")
        else:
            print("Prompt tokens: N/A")
            print("Response tokens: N/A")
        print()
        print(response_content)
    else:
        print(response_content)


if __name__ == "__main__":
    main()
