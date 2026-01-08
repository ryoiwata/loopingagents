import os
import subprocess


run_python_file_schema = {
    "type": "function",
    "function": {
        "name": "run_python_file",
        "description": "Executes a Python file.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": (
                        "Python file path to execute, relative to the "
                        "working directory"
                    ),
                },
                "args": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "Optional list of command-line arguments to pass "
                        "to the script"
                    ),
                },
            },
            "required": ["file_path"],
        },
    },
}


def run_python_file(working_directory, file_path, args=None):
    """
    Execute a Python file with security guardrails.

    Args:
        working_directory: The base working directory that serves as the root
        file_path: The Python file path to execute (relative to
                   working_directory)
        args: Optional list of command-line arguments to pass to the script

    Returns:
        A string with execution output or an error message prefixed with
        "Error:"
    """
    try:
        # Get absolute path of working_directory
        working_dir_abs = os.path.abspath(working_directory)

        # Construct target_file by joining the absolute working directory
        # and file_path
        target_file = os.path.join(working_dir_abs, file_path)

        # Normalize the path to prevent directory traversal
        target_file = os.path.normpath(target_file)

        # Validation: Ensure target is inside the permitted directory
        try:
            common_path = os.path.commonpath([working_dir_abs, target_file])
            if common_path != working_dir_abs:
                return (
                    f'Error: Cannot execute "{file_path}" as it is outside '
                    f'the permitted working directory'
                )
        except ValueError:
            # This can happen on Windows with different drives
            return (
                f'Error: Cannot execute "{file_path}" as it is outside '
                f'the permitted working directory'
            )

        # Check if target_file is a regular file
        if not os.path.isfile(target_file):
            return (
                f'Error: "{file_path}" does not exist or is not a regular file'
            )

        # Check if file ends with .py
        if not file_path.endswith(".py"):
            return f'Error: "{file_path}" is not a Python file'

        # Construct command list
        command = ["python", target_file]
        if args is not None:
            command.extend(args)

        # Run the Python file using subprocess
        result = subprocess.run(
            command,
            cwd=working_dir_abs,
            capture_output=True,
            text=True,
            timeout=30
        )

        # Format output
        output_parts = []

        # Add return code if non-zero
        if result.returncode != 0:
            output_parts.append(
                f"Process exited with code {result.returncode}"
            )

        # Handle stdout and stderr
        if not result.stdout and not result.stderr:
            return "No output produced"

        if result.stdout:
            output_parts.append(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            output_parts.append(f"STDERR:\n{result.stderr}")

        return "\n".join(output_parts)

    except subprocess.TimeoutExpired:
        return "Error: executing Python file: Process timed out after 30 seconds"
    except Exception as e:
        return f"Error: executing Python file: {e}"

