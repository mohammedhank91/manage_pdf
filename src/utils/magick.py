import os
import sys
import subprocess
import logging

def find_imagick(self):
    """
    Locate the portable ImageMagick exe, or fallback to 'magick'.
    Returns the path to the executable.
    """
    # Try all possible locations for ImageMagick
    possible_paths = []
    
    # Get the base directory
    base = self._app_base()
    
    # Add possible paths for frozen/PyInstaller environment
    if getattr(sys, "frozen", False):
        # 1. Try in the same directory as the executable
        possible_paths.extend([
            os.path.join(base, "imagick_portable_64", "magick.exe"),
            os.path.join(base, "magick.exe"),
        ])
        
        # 2. Try in various relative paths from executable
        for rel_path in [".", "..", "../..", "../../.."]:
            possible_paths.append(os.path.join(base, rel_path, "imagick_portable_64", "magick.exe"))
    else:
        # Running as script - try various relative paths
        for rel_path in [".", "..", "../.."]:
            possible_paths.append(os.path.join(base, rel_path, "imagick_portable_64", "magick.exe"))
    
    # Also look in APPDATA directories which is where it might be extracted by the installer
    appdata = os.environ.get('APPDATA', '')
    localappdata = os.environ.get('LOCALAPPDATA', '')
    programfiles = os.environ.get('PROGRAMFILES', '')
    
    if appdata:
        possible_paths.append(os.path.join(appdata, "PDF Manager", "imagick_portable_64", "magick.exe"))
    if localappdata:
        possible_paths.append(os.path.join(localappdata, "PDF Manager", "imagick_portable_64", "magick.exe"))
    if programfiles:
        possible_paths.append(os.path.join(programfiles, "PDF Manager", "imagick_portable_64", "magick.exe"))
    
    # Log the search process
    logging.info(f"Searching for ImageMagick executable in {len(possible_paths)} possible locations")
    for i, path in enumerate(possible_paths):
        logging.info(f"Location #{i+1}: {path}")
        if os.path.isfile(path):
            logging.info(f"✓ Found ImageMagick at: {path}")
            return path
        else:
            logging.info(f"✗ Not found at: {path}")
            
    # If we get here, check if there's any magick.exe in the application directory
    # This is to handle PyInstaller bundling situation
    if getattr(sys, "frozen", False):
        for root, dirs, files in os.walk(base):
            for file in files:
                if file.lower() == "magick.exe":
                    full_path = os.path.join(root, file)
                    logging.info(f"✓ Found ImageMagick by directory scan at: {full_path}")
                    return full_path
    
    # Last resort - try system "magick" command
    logging.warning("⚠ ImageMagick not found in any expected location, defaulting to system 'magick'")
    return "magick"

def run_imagemagick(self, cmd):
    """Run an ImageMagick command with the portable executable if available."""
    magick_path = self.find_imagick()
    
    # Replace 'magick' with the full path to the portable executable
    if 'magick -' in cmd:
        invocation = cmd.replace('magick -', f'"{magick_path}" -', 1)
    elif cmd.startswith('magick '):
        invocation = cmd.replace('magick ', f'"{magick_path}" ', 1)
    else:
        invocation = cmd
    
    logging.info(f"Executing ImageMagick: {invocation}")
    
    try:
        # Set environment variables
        env = os.environ.copy()
        
        # Add ImageMagick parameters to force using built-in delegates instead of Ghostscript
        if 'pdf' in invocation.lower():
            # For PDF operations, use internal delegate libraries
            if not '-alpha off' in invocation:
                invocation = invocation.replace('magick', 'magick -alpha off')
        
        result = subprocess.run(
            invocation, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True,
            check=True,
            env=env
        )
        return result
    except subprocess.CalledProcessError as e:
        stderr = e.stderr if hasattr(e, 'stderr') else ""
        logging.error(f"ImageMagick failed ({e.returncode}): {stderr}")
        
        # Check for common error patterns - simplified without Ghostscript dependency
        if "not recognized" in str(stderr).lower():
            raise RuntimeError(
                f"ImageMagick not found. Please place 'imagick_portable...' next to the app."
            )
        
        # Generic error
        raise RuntimeError(f"ImageMagick error: {stderr}")
