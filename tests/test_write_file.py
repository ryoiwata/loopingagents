import os
import sys

# Add root and src directories to Python path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(root_dir, "src"))
sys.path.insert(0, root_dir)

from agent_core.tools.write_file import write_file  # noqa: E402


def main():
    # Test 1: Overwriting an existing file
    print("Test 1: Overwriting existing file - lorem.txt")
    result = write_file(
        "calculator", "lorem.txt", "wait, this isn't lorem ipsum"
    )
    print(f"Result: {result}")
    if result.startswith("Error:"):
        print("✗ Failed to write file")
    else:
        print("✓ File written successfully")
        # Verify the content
        with open("calculator/lorem.txt", "r") as f:
            content = f.read()
            if content == "wait, this isn't lorem ipsum":
                print("✓ Content verified correctly")
            else:
                expected = "wait, this isn't lorem ipsum"
                print(
                    f"✗ Content mismatch. Expected: '{expected}', "
                    f"Got: '{content[:50]}...'"
                )
    print()

    # Test 2: Writing to a sub-directory
    print("Test 2: Writing to sub-directory - pkg/morelorem.txt")
    result = write_file(
        "calculator",
        "pkg/morelorem.txt",
        "lorem ipsum dolor sit amet"
    )
    print(f"Result: {result}")
    if result.startswith("Error:"):
        print("✗ Failed to write file")
    else:
        print("✓ File written successfully")
        # Verify the file exists and has correct content
        file_path = "calculator/pkg/morelorem.txt"
        if os.path.isfile(file_path):
            with open(file_path, "r") as f:
                content = f.read()
                if content == "lorem ipsum dolor sit amet":
                    print("✓ Content verified correctly")
                else:
                    expected = "lorem ipsum dolor sit amet"
                    print(
                        f"✗ Content mismatch. Expected: '{expected}', "
                        f"Got: '{content}'"
                    )
        else:
            print("✗ File was not created")
    print()

    # Test 3: Security guardrail - trying to write outside working directory
    print("Test 3: Security check - trying to write to /tmp/temp.txt")
    result = write_file(
        "calculator", "/tmp/temp.txt", "this should not be allowed"
    )
    print(f"Result: {result}")
    if result.startswith("Error:") and "outside" in result:
        print("✓ Security check passed - file write was blocked")
    else:
        print("✗ Security check FAILED - file write should be blocked")
        # Check if file was actually created (it shouldn't be)
        if os.path.isfile("/tmp/temp.txt"):
            print("✗ CRITICAL: File was created outside working directory!")
            # Clean up if it was created
            os.remove("/tmp/temp.txt")
    print()


if __name__ == "__main__":
    main()
