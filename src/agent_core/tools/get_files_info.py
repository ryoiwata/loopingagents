import argparse
import os


get_files_info_schema = {
    "type": "function",
    "function": {
        "name": "get_files_info",
        "description": (
            "Lists files in a specified directory relative to the working "
            "directory, providing file size and directory status"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": (
                        "Directory path to list files from, relative to the "
                        "working directory (default is '.')"
                    ),
                },
            },
            "required": [],
        },
    },
}


def get_files_info(working_directory, directory="."):
    """
    Get information about files in a directory with security guardrails.

    Args:
        working_directory: The base working directory that serves as the root
        directory: The directory to list (relative to working_directory)

    Returns:
        A string with file information or an error message prefixed with
        "Error:"
    """
    try:
        # Get absolute path of working_directory
        working_dir_abs = os.path.abspath(working_directory)

        # Construct target_dir by joining the absolute working directory
        # and directory
        target_dir = os.path.join(working_dir_abs, directory)

        # Normalize the path to prevent directory traversal
        target_dir = os.path.normpath(target_dir)

        # Validation: Ensure target is inside the permitted directory
        try:
            common_path = os.path.commonpath([working_dir_abs, target_dir])
            if common_path != working_dir_abs:
                return (
                    f'Error: Cannot list "{directory}" as it is outside '
                    f'the permitted working directory'
                )
        except ValueError:
            # This can happen on Windows with different drives
            return (
                f'Error: Cannot list "{directory}" as it is outside '
                f'the permitted working directory'
            )

        # Check if target_dir is a directory
        if not os.path.isdir(target_dir):
            return f'Error: "{directory}" is not a directory'

        # Iterate through items in the directory
        results = []
        items = sorted(os.listdir(target_dir))

        for item in items:
            item_path = os.path.join(target_dir, item)
            try:
                size = os.path.getsize(item_path)
                is_dir = os.path.isdir(item_path)
                results.append(
                    f"- {item}: file_size={size} bytes, is_dir={is_dir}"
                )
            except (OSError, PermissionError):
                # Skip items we can't access
                continue

        # Return formatted string with each item on a new line
        return "\n".join(results) if results else ""

    except Exception as e:
        return f"Error: {str(e)}"


def main():
    """Command-line interface for get_files_info."""
    parser = argparse.ArgumentParser(
        description=(
            "Get information about files in a directory with "
            "security guardrails"
        )
    )
    parser.add_argument(
        "working_directory",
        type=str,
        help="The base working directory that serves as the root"
    )
    parser.add_argument(
        "directory",
        type=str,
        nargs="?",
        default=".",
        help=(
            "The directory to list (relative to working_directory). "
            "Defaults to '.'"
        )
    )
    args = parser.parse_args()

    result = get_files_info(args.working_directory, args.directory)
    print(result)


if __name__ == "__main__":
    main()
