import os
import sys

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from agent_core.tools.get_files_info import get_files_info  # noqa: E402


def main():
    working_dir = "calculator"
    root_contents = get_files_info(working_dir)
    print(root_contents)
    pkg_contents = get_files_info(working_dir, "pkg")
    print(pkg_contents)
    pkg_contents = get_files_info(working_dir, "/bin")
    print(pkg_contents)


if __name__ == "__main__":
    main()
