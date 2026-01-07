import os
import sys

# Add root and src directories to Python path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(root_dir, "src"))
sys.path.insert(0, root_dir)

from agent_core.tools.run_python_file import run_python_file  # noqa: E402


def main():
    # Test 1: Run main.py without arguments
    print("Test 1: Running calculator/main.py without arguments")
    result = run_python_file("calculator", "main.py")
    print(f"Result:\n{result}")
    if result.startswith("Error:"):
        print("✗ Failed to execute file")
    else:
        print("✓ File executed successfully")
    print()

    # Test 2: Run main.py with arguments
    print("Test 2: Running calculator/main.py with arguments ['3 + 5']")
    result = run_python_file("calculator", "main.py", ["3 + 5"])
    print(f"Result:\n{result}")
    if result.startswith("Error:"):
        print("✗ Failed to execute file")
    else:
        print("✓ File executed successfully")
    print()

    # Test 3: Run tests.py
    print("Test 3: Running calculator/tests.py")
    result = run_python_file("calculator", "tests.py")
    print(f"Result:\n{result}")
    if result.startswith("Error:"):
        print("✗ Failed to execute file")
    else:
        print("✓ File executed successfully")
    print()

    # Test 4: Security check - trying to execute ../main.py
    print("Test 4: Security check - trying to execute ../main.py")
    result = run_python_file("calculator", "../main.py")
    print(f"Result: {result}")
    if result.startswith("Error:") and "outside" in result:
        print("✓ Security check passed - execution was blocked")
    else:
        print("✗ Security check FAILED - execution should be blocked")
    print()

    # Test 5: Security check - trying to execute nonexistent.py
    print("Test 5: Security check - trying to execute nonexistent.py")
    result = run_python_file("calculator", "nonexistent.py")
    print(f"Result: {result}")
    if result.startswith("Error:") and "does not exist" in result:
        print("✓ Error handling passed - file not found")
    else:
        print("✗ Error handling FAILED - should return error")
    print()

    # Test 6: Security check - trying to execute lorem.txt (not a Python file)
    print("Test 6: Security check - trying to execute lorem.txt")
    result = run_python_file("calculator", "lorem.txt")
    print(f"Result: {result}")
    if result.startswith("Error:") and "not a Python file" in result:
        print("✓ Extension check passed - non-Python file rejected")
    else:
        print("✗ Extension check FAILED - should reject non-Python file")
    print()


if __name__ == "__main__":
    main()
