import os
import subprocess
import logging


def find_imagick(self):
    """
    Locate the portable ImageMagick exe, or fallback to 'magick'.
    Returns the path to the executable.
    """
    # Get the project root directory (one level up from src)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    print(f"Project root: {project_root}")

    # Primary location for portable ImageMagick
    portable_magick = os.path.join(project_root, "imagick_portable_64", "magick.exe")

    if os.path.exists(portable_magick):
        print(f"Found ImageMagick at: {portable_magick}")
        return portable_magick

    # If not found in primary location, try system command
    print("ImageMagick not found in portable location, defaulting to system 'magick'")
    return "magick"


def run_imagemagick(self, cmd):
    """Run an ImageMagick command with the portable executable if available."""
    # Get the path to ImageMagick directly using the project root
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    portable_magick = os.path.join(project_root, "imagick_portable_64", "magick.exe")

    # Check if it exists
    if os.path.exists(portable_magick):
        magick_path = portable_magick
        print(f"Using portable ImageMagick: {portable_magick}")
    else:
        magick_path = "magick"
        print(f"Portable ImageMagick not found at {portable_magick}, falling back to 'magick' command")

    # Replace 'magick' with the full path to the executable if needed
    if magick_path != 'magick':
        # Quote the path to handle spaces
        if 'magick -' in cmd:
            invocation = cmd.replace('magick -', f'"{magick_path}" -', 1)
        elif cmd.startswith('magick '):
            invocation = cmd.replace('magick ', f'"{magick_path}" ', 1)
        else:
            invocation = cmd
    else:
        # Just use the command as is
        invocation = cmd

    print(f"Executing ImageMagick command: {invocation}")

    try:
        # Set environment variables
        env = os.environ.copy()

        # Simplify command for testing if there are issues
        if " -page " in invocation and " -density " in invocation:
            print("Simplifying command for better compatibility...")
            # Remove complex options that might cause issues
            invocation = invocation.replace(" -page ", " ")

        result = subprocess.run(
            invocation,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
            env=env
        )
        print("ImageMagick command executed successfully")
        return result
    except subprocess.CalledProcessError as e:
        stderr = e.stderr if hasattr(e, 'stderr') else ""
        stdout = e.stdout if hasattr(e, 'stdout') else ""

        # Show more detailed error information
        error_info = f"Exit code: {e.returncode}\nStdout: {stdout}\nStderr: {stderr}"
        logging.error(f"ImageMagick failed: {error_info}")
        print(f"ImageMagick command failed: {error_info}")

        # Check for common error patterns
        if "not recognized" in str(stderr).lower():
            raise RuntimeError(
                "ImageMagick not found. Please ensure the portable version is available in the imagick_portable_64 folder."
            )
        elif "cannot find the path" in str(stderr).lower():
            raise RuntimeError(
                "ImageMagick error: The system cannot find one of the paths in the command. Check that all files exist."
            )

        # Generic error
        raise RuntimeError(f"ImageMagick error: {stderr}")


def run_pytest():
    """Run pytest and capture errors."""
    import pytest
    result = pytest.main(["--maxfail=1", "--disable-warnings", "-q"])
    if result != 0:
        logging.error("Pytest encountered errors.")
    return result


if __name__ == "__main__":
    run_pytest()
