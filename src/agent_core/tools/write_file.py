import os


write_file_schema = {
    "type": "function",
    "function": {
        "name": "write_file",
        "description": "Writes or overwrites content to a file.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": (
                        "File path to write, relative to the working directory"
                    ),
                },
                "content": {
                    "type": "string",
                    "description": "Content string to write to the file",
                },
            },
            "required": ["file_path", "content"],
        },
    },
}


def write_file(working_directory, file_path, content):
    """
    Write content to a file with security guardrails.

    Args:
        working_directory: The base working directory that serves as the root
        file_path: The file path to write (relative to working_directory)
        content: The content string to write to the file

    Returns:
        A success message or an error message prefixed with "Error:"
    """
    try:
        # Get absolute path of working_directory
        working_dir_abs = os.path.abspath(working_directory)

        # Construct target_path by joining the absolute working directory
        # and file_path
        target_path = os.path.join(working_dir_abs, file_path)

        # Normalize the path to prevent directory traversal
        target_path = os.path.normpath(target_path)

        # Validation: Ensure target is inside the permitted directory
        try:
            common_path = os.path.commonpath([working_dir_abs, target_path])
            if common_path != working_dir_abs:
                return (
                    f'Error: Cannot write to "{file_path}" as it is outside '
                    f'the permitted working directory'
                )
        except ValueError:
            # This can happen on Windows with different drives
            return (
                f'Error: Cannot write to "{file_path}" as it is outside '
                f'the permitted working directory'
            )

        # Check if target_path points to an existing directory
        if os.path.isdir(target_path):
            return (
                f'Error: Cannot write to "{file_path}" as it is a directory'
            )

        # Ensure all parent directories exist
        parent_dir = os.path.dirname(target_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)

        # Write the file
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)

        # Return success message
        return (
            f'Successfully wrote to "{file_path}" '
            f'({len(content)} characters written)'
        )

    except Exception as e:
        return f"Error: {str(e)}"

