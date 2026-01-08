# AI Agent with File System Tools

A robust, multi-turn AI agent that uses OpenAI's function calling capabilities to interact with the local file system and execute Python scripts. Built with LangChain, this agent maintains conversation history and can perform complex workflows through iterative tool execution.

## Project Overview

This AI Agent is a command-line tool that enables an LLM to safely interact with your local file system through a set of secure, sandboxed tools. The agent uses a feedback loop architecture where it can:

- **List files and directories** to explore the project structure
- **Read file contents** to understand code and documentation
- **Write or update files** to create or modify project files
- **Execute Python scripts** with optional command-line arguments

The agent maintains full conversation history across multiple iterations, allowing it to perform complex multi-step tasks that require sequential tool calls and decision-making.

## Core Features

### File System Operations

- **`get_files_info`**: List files and directories with size information and directory status
- **`get_file_content`**: Read file contents (with automatic truncation for large files)
- **`write_file`**: Create or overwrite files, with automatic directory creation
- **`run_python_file`**: Execute Python scripts with timeout protection and output capture

### Agent Capabilities

- **Multi-turn conversations**: Maintains conversation history across up to 20 iterations
- **Automatic tool selection**: LLM intelligently chooses which tools to use based on user requests
- **Iterative problem-solving**: Can perform complex workflows requiring multiple tool calls
- **Structured logging**: All interactions are logged to timestamped JSON files
- **Verbose mode**: Detailed output showing each iteration, tool call, and result

## Architecture

### Agent Loop (Feedback Loop)

The agent operates using a **feedback loop** pattern:

1. **Initialization**: The conversation starts with a system message and the user's prompt
2. **Iteration Loop** (max 20 iterations):
   - The LLM is invoked with the current message history
   - The model's response (AIMessage) is appended to the conversation history
   - If the response contains `tool_calls`:
     - Each tool call is executed using `call_function()`
     - Tool results are wrapped in `ToolMessage` objects
     - Tool messages are appended to the conversation history
     - The loop continues to process tool results
   - If the response contains a final text answer (no tool calls):
     - The response is extracted and printed
     - The loop breaks
3. **Error Handling**: If 20 iterations are reached without a final answer, the agent exits with an error

### Tool Execution Flow

```
User Query → LLM → Tool Calls → Function Execution → Tool Results → LLM → Final Answer
```

1. **Tool Declaration**: Tools are defined using OpenAI's function calling schema format
2. **Tool Binding**: Tools are bound to the LLM using LangChain's `bind_tools()` method
3. **Tool Selection**: The LLM automatically selects appropriate tools based on the user's request
4. **Security Injection**: The `working_directory` parameter is automatically injected for all tool calls
5. **Result Integration**: Tool results are added to the conversation as `ToolMessage` objects

### Technology Stack

- **LangChain**: Prompt management, message handling, and LLM integration
- **OpenAI API**: LLM provider with function calling support
- **Python**: Core implementation language
- **YAML**: Configuration and system prompt storage

## Security & Guardrails

The agent implements multiple layers of security to prevent unauthorized file system access:

### Working Directory Injection

All tool calls automatically receive a `working_directory` parameter set to the project root. This ensures operations are confined to the project directory:

```python
# In call_function.py
args_copy["working_directory"] = get_project_root()
```

### Path Normalization

All file paths are normalized using `os.path.normpath()` to prevent directory traversal attacks:

```python
target_path = os.path.normpath(os.path.join(working_dir_abs, file_path))
```

### Path Validation

Before any file operation, the agent validates that the target path is within the permitted working directory using `os.path.commonpath()`:

```python
common_path = os.path.commonpath([working_dir_abs, target_path])
if common_path != working_dir_abs:
    return f'Error: Cannot access "{file_path}" as it is outside the permitted working directory'
```

### Additional Security Measures

- **File Type Validation**: `run_python_file` only executes files ending with `.py`
- **Timeout Protection**: Python script execution has a 30-second timeout
- **Error Handling**: All errors are caught and returned as user-friendly error messages
- **File Size Limits**: File reading is limited to `MAX_CHARS` (default: 10,000 characters) with truncation warnings

## Configuration

### System Prompts

System prompts are stored as YAML files in the `system_prompts/` directory. Each prompt file contains:

- **`version`**: Prompt version identifier
- **`template`**: The system prompt text
- **`parameters`**: Model parameters (e.g., `temperature`)

Example (`system_prompts/v1_helpful_coding_agent.yaml`):

```yaml
version: "v1_helpful_coding_agent"
template: |
  You are a helpful AI coding agent.
  
  When a user asks a question or makes a request, prioritize direct action over exploration.
  ...
parameters:
  temperature: 0
```

### Settings Configuration

Global settings are stored in `config/settings.yaml`:

```yaml
active_prompt: "v1_helpful_coding_agent"
MAX_CHARS: 10000
```

- **`active_prompt`**: The system prompt to use (must match a file in `system_prompts/`)
- **`MAX_CHARS`**: Maximum characters to read from a file before truncation

### Environment Variables

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

## Installation & Usage

### Prerequisites

- Python 3.8+
- `uv` package manager (recommended) or `pip`

### Installation

Using `uv`:

```bash
# Install dependencies
uv sync

# Activate the environment
source .venv/bin/activate  # On Linux/Mac
# or
.venv\Scripts\activate  # On Windows
```

Using `pip`:

```bash
pip install langchain langchain-openai python-dotenv pyyaml
```

### Basic Usage

Run the agent with a query:

```bash
python src/agent_core/main.py --query "List all Python files in the calculator directory"
```

### Command-Line Options

- **`--query`**: The prompt/query to send to the agent (default: sample engineering tips question)
- **`--verbose`**: Enable verbose output showing iterations, tool calls, and results

### Usage Examples

**Example 1: List files in a directory**

```bash
python src/agent_core/main.py --query "Show me what's in the calculator directory"
```

**Example 2: Read and analyze a file**

```bash
python src/agent_core/main.py --query "Read calculator/main.py and explain what it does"
```

**Example 3: Execute a Python script**

```bash
python src/agent_core/main.py --query "Run calculator/main.py with the argument '3 + 5'"
```

**Example 4: Complex multi-step task**

```bash
python src/agent_core/main.py --query "Read calculator/tests.py, run it, and tell me if all tests pass"
```

**Example 5: Verbose mode**

```bash
python src/agent_core/main.py --query "List files in calculator" --verbose
```

Output will show:
- Initial messages
- Each iteration number
- Tool calls being made
- Tool results
- Final response
- Token usage statistics

## Project Structure

```
loopingagents/
├── src/
│   └── agent_core/
│       ├── main.py                 # Main entry point and agent loop
│       ├── call_function.py       # Tool execution and registry
│       ├── providers/
│       │   └── prompt_loader.py   # YAML prompt loading
│       └── tools/
│           ├── get_files_info.py  # List files tool
│           ├── get_file_content.py # Read file tool
│           ├── run_python_file.py # Execute Python tool
│           └── write_file.py      # Write file tool
├── config/
│   └── settings.yaml              # Global configuration
├── system_prompts/
│   ├── v1_helpful_coding_agent.yaml
│   └── v1_robot.yaml
├── calculator/                    # Example test project
│   ├── main.py
│   ├── tests.py
│   └── pkg/
├── logs/                          # Session logs (JSON format)
└── README.md
```

## Logging

All agent interactions are logged to timestamped JSON files in the `logs/` directory. Each log entry contains:

- **`timestamp`**: ISO 8601 format timestamp
- **`model`**: The LLM model used
- **`system_prompt`**: The full system prompt template
- **`prompt`**: The user's query
- **`response`**: The final model response
- **`usage`**: Token usage statistics (prompt_tokens, completion_tokens)

Example log file: `logs/session_20260107_183932.json`

## Error Handling

The agent handles various error conditions:

- **Maximum iterations reached**: Exits with error code 1 if 20 iterations complete without a final answer
- **Temperature=0 not supported**: Automatically retries with default temperature for models that don't support it
- **Invalid file paths**: Returns user-friendly error messages for security violations
- **Tool execution errors**: Catches and reports exceptions from tool functions

## Contributing

When adding new tools:

1. Create a new file in `src/agent_core/tools/`
2. Define the tool schema in OpenAI function format
3. Implement the tool function with security guardrails
4. Add the schema to `available_tools` in `call_function.py`
5. Add the function to `function_map` in `call_function.py`
6. Update the system prompt to mention the new tool

## License

See `LICENSE` file for details.
