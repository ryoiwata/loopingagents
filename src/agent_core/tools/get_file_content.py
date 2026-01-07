import os
from config import MAX_CHARS


def get_file_content(working_directory, file_path):
    """
    Get the content of a file with security guardrails.

    Args:
        working_directory: The base working directory that serves as the root
        file_path: The file path to read (relative to working_directory)

    Returns:
        A string with file content or an error message prefixed with "Error:"
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
                    f'Error: Cannot read "{file_path}" as it is outside '
                    f'the permitted working directory'
                )
        except ValueError:
            # This can happen on Windows with different drives
            return (
                f'Error: Cannot read "{file_path}" as it is outside '
                f'the permitted working directory'
            )

        # Check if target_file is a regular file
        if not os.path.isfile(target_file):
            return (
                f'Error: File not found or is not a regular file: "{file_path}"'
            )

        # Read file content with MAX_CHARS limit
        with open(target_file, "r", encoding="utf-8") as f:
            content = f.read(MAX_CHARS)
            # Check if file was truncated
            remaining = f.read(1)
            if remaining:
                content += (
                    f'\n[...File "{file_path}" truncated at {MAX_CHARS} '
                    f'characters]'
                )

        return content

    except Exception as e:
        return f"Error: {str(e)}"

