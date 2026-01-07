import os
import sys

# Add root and src directories to Python path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(root_dir, "src"))
sys.path.insert(0, root_dir)

from agent_core.tools.get_file_content import get_file_content  # noqa: E402


def main():
    # Test 1: Verify truncation message appears for lorem.txt
    print("Test 1: Reading lorem.txt (should be truncated)")
    result = get_file_content("calculator", "lorem.txt")
    if "truncated at" in result:
        print("✓ Truncation message found")
    else:
        print("✗ Truncation message NOT found")
    print(f"Result length: {len(result)} characters")
    print(f"First 100 chars: {result[:100]}...")
    print()

    # Test 2: Valid file - main.py
    print("Test 2: Reading valid file - main.py")
    result = get_file_content("calculator", "main.py")
    if result.startswith("Error:"):
        print(f"✗ Error: {result}")
    else:
        print("✓ File read successfully")
        print(f"First 100 chars: {result[:100]}...")
    print()

    # Test 3: Valid file - pkg/calculator.py
    print("Test 3: Reading valid file - pkg/calculator.py")
    result = get_file_content("calculator", "pkg/calculator.py")
    if result.startswith("Error:"):
        print(f"✗ Error: {result}")
    else:
        print("✓ File read successfully")
        print(f"First 100 chars: {result[:100]}...")
    print()

    # Test 4: Invalid file - /bin/cat (outside working directory)
    print("Test 4: Reading invalid file - /bin/cat (outside directory)")
    result = get_file_content("calculator", "/bin/cat")
    if result.startswith("Error:"):
        print(f"✓ Security check passed: {result}")
    else:
        print("✗ Security check FAILED - file should be rejected")
    print()

    # Test 5: Invalid file - pkg/does_not_exist.py
    print("Test 5: Reading non-existent file - pkg/does_not_exist.py")
    result = get_file_content("calculator", "pkg/does_not_exist.py")
    if result.startswith("Error:"):
        print(f"✓ Error handling passed: {result}")
    else:
        print("✗ Error handling FAILED - should return error")
    print()


if __name__ == "__main__":
    main()
