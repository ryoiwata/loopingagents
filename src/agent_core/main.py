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
from agent_core.call_function import (  # noqa: E402
    available_tools,
    call_function,
)
from langchain_core.messages import ToolMessage  # noqa: E402


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

    # Bind tools to the model with auto tool selection
    llm_with_tools = llm.bind_tools(available_tools, tool_choice="auto")

    # Format messages using the template
    formatted_messages = chat_template.format_messages(user_input=prompt)

    # Print full messages list to console before API call
    print("=" * 80)
    print("Messages being sent to OpenAI API:")
    print("=" * 80)
    for i, msg in enumerate(formatted_messages, 1):
        print(f"\nMessage {i}:")
        print(f"  Type: {msg.type}")
        print(f"  Content: {msg.content}")
    print("=" * 80)
    print()

    # Invoke the model with tools
    try:
        response = llm_with_tools.invoke(formatted_messages)
    except Exception as e:
        # If temperature=0 is not supported, retry with default temperature
        if "temperature" in str(e).lower() and temperature == 0:
            # Use default temperature
            llm = ChatOpenAI(model=model)
            llm_with_tools = llm.bind_tools(
                available_tools, tool_choice="auto"
            )
            response = llm_with_tools.invoke(formatted_messages)
        else:
            raise

    # Handle tool calls if present
    response_content = None
    if hasattr(response, "tool_calls") and response.tool_calls:
        # Add the AI response with tool calls to message history
        formatted_messages.append(response)

        # Execute each tool call
        for tool_call in response.tool_calls:
            # Call the function and get the result
            result_dict = call_function(tool_call, verbose=args.verbose)

            # Extract tool_call_id for ToolMessage
            if isinstance(tool_call, dict):
                tool_call_id = (
                    tool_call.get("id") or
                    tool_call.get("tool_call_id") or
                    f"call_{id(tool_call)}"
                )
            else:
                tool_call_id = getattr(
                    tool_call, "id",
                    getattr(tool_call, "tool_call_id", f"call_{id(tool_call)}")
                )

            # Create ToolMessage and add to message history
            tool_message = ToolMessage(
                content=result_dict["content"],
                tool_call_id=tool_call_id
            )
            formatted_messages.append(tool_message)

            # Print result if verbose
            if args.verbose:
                print(f"-> {result_dict['content']}")

        # Continue the conversation with tool results
        # Invoke the model again with the updated message history
        try:
            response = llm_with_tools.invoke(formatted_messages)
            # Extract content from the final response
            response_content = response.content
        except Exception as e:
            # If temperature=0 is not supported, retry with default temp
            if "temperature" in str(e).lower() and temperature == 0:
                llm = ChatOpenAI(model=model)
                llm_with_tools = llm.bind_tools(
                    available_tools, tool_choice="auto"
                )
                response = llm_with_tools.invoke(formatted_messages)
                response_content = response.content
            else:
                raise
    else:
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
        # Only print response_content if it exists (not None for tool calls)
        if response_content is not None:
            print(response_content)
    else:
        # Only print response_content if it exists (not None for tool calls)
        if response_content is not None:
            print(response_content)


if __name__ == "__main__":
    main()
