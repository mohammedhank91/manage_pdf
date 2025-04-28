import sys
import os
import subprocess
import logging
from pathlib import Path
import argparse


def ensure_tool_installed(module_name: str):
    try:
        __import__(module_name)
    except ImportError:
        logging.info(f"Installing {module_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", module_name])


def has_executable(directory: Path, exec_names: list[str]) -> bool:
    """
    Check if any executable in exec_names exists in directory, its 'bin', or 'library/bin' subdirectories.
    """
    for name in exec_names:
        path1 = directory / name
        path2 = directory / 'bin' / name
        path3 = directory / 'library' / 'bin' / name
        if path1.exists():
            logging.info(f"Found {name} at {path1}")
            return True
        if path2.exists():
            logging.info(f"Found {name} at {path2}")
            return True
        if path3.exists():
            logging.info(f"Found {name} at {path3}")
            return True
    logging.warning(f"No executables {exec_names} found in {directory}")
    return False


def build_executable(
    script: Path,
    icon: Path,
    work_dir: Path,
    dist_dir: Path,
    extras: list[tuple[str, str]],
    name: str = "PDFManager",
    windowed: bool = True,
):
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        f"--name={name}",
        "--clean",
        "--noconfirm",
        "--noconsole",
    ]
    if windowed:
        cmd.append("--windowed")
    if icon.exists():
        cmd.append(f"--icon={icon}")
    cmd += [f"--workpath={work_dir}", f"--distpath={dist_dir}"]

    # Hidden imports
    hidden = ["PIL", "PyPDF2", "pikepdf", "pdf2image", "xml", "xml.dom"]
    for module in hidden:
        cmd.append(f"--hidden-import={module}")

    # Data extras (portable binaries)
    for src, dest in extras:
        cmd.append(f"--add-data={src}{os.pathsep}{dest}")

    cmd.append(str(script))

    logging.info("Running PyInstaller command: %s", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logging.error("Build failed (code %s).", result.returncode)
        logging.error("STDOUT: %s", result.stdout)
        logging.error("STDERR: %s", result.stderr)
        sys.exit(result.returncode)

    logging.info("Build succeeded. Executable at %s", dist_dir / name)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    parser = argparse.ArgumentParser(description="Build PDFManager standalone executable.")
    parser.add_argument("--icon", type=Path, default=Path("src/resources/manage_pdf.ico"), help="Path to icon file.")
    parser.add_argument("--imagick", type=Path, default=Path("imagick_portable_64"), help="ImageMagick directory.")
    parser.add_argument("--poppler", type=Path, default=Path("poppler_portable_64"), help="Poppler directory.")
    parser.add_argument("--workpath", type=Path, default=Path("build"), help="PyInstaller work path.")
    parser.add_argument("--distpath", type=Path, default=Path("dist"), help="PyInstaller dist path.")
    parser.add_argument("--name", default="PDFManager", help="Name for the executable.")
    parser.add_argument("--windowed", action="store_true", help="Build as windowed app.")
    args = parser.parse_args()

    # Ensure PyInstaller is installed
    ensure_tool_installed("PyInstaller")

    # Collect portable extras without requiring PATH
    extras: list[tuple[str, str]] = []

    # ImageMagick portable
    if args.imagick.exists():
        if has_executable(args.imagick, ["magick.exe", "convert.exe"]):
            extras.append((str(args.imagick), "imagick_portable_64"))
        else:
            logging.warning(f"ImageMagick executables not found in {args.imagick}")
    else:
        logging.warning(f"ImageMagick directory not found at {args.imagick}")

    # Poppler portable
    if args.poppler.exists():
        if has_executable(args.poppler, ["pdftoppm.exe", "pdftocairo.exe"]):
            extras.append((str(args.poppler), "poppler_portable_64"))
        else:
            logging.warning(f"Poppler executables not found in {args.poppler}")
    else:
        logging.warning(f"Poppler directory not found at {args.poppler}")

    # Entry script
    script_file = Path("run_app.py")

    # Build
    build_executable(
        script=script_file,
        icon=args.icon,
        work_dir=args.workpath,
        dist_dir=args.distpath,
        extras=extras,
        name=args.name,
        windowed=args.windowed,
    )

    logging.info("To create installer, run ISCC on build_tools/PDFManager_PyInstaller_Setup.iss")
