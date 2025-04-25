# build_tools/build_with_pyinstaller.py
#!/usr/bin/env python3
import sys
import os
import subprocess
import logging
from pathlib import Path
import argparse

# Determine project root (one level up from this script)
project_root = Path(__file__).resolve().parent.parent


def ensure_tool_installed(module_name: str):
    try:
        __import__(module_name)
    except ImportError:
        logging.info(f"Installing {module_name}... Accessing PyPI.")
        subprocess.check_call([sys.executable, "-m", "pip", "install", module_name])


def has_executable(directory: Path, exec_names: list[str]) -> bool:
    """
    Check for executables in directory, its 'bin', or 'library/bin'.
    """
    for name in exec_names:
        for sub in [directory, directory / 'bin', directory / 'library' / 'bin']:
            candidate = sub / name
            if candidate.exists():
                logging.info(f"Found {name} at {candidate}")
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
    cmd = [sys.executable, "-m", "PyInstaller", f"--name={name}", "--clean", "--noconfirm"]
    if windowed:
        cmd.append("--windowed")
        # no console
        cmd.append("--noconsole")
    if icon.exists():
        cmd.append(f"--icon={icon}")
    cmd += [f"--workpath={work_dir}", f"--distpath={dist_dir}"]

    # Hidden imports for Qt and PDF tools
    hidden = [
        "PIL", "PyPDF2", "pikepdf", "pdf2image", "xml", "xml.dom",
        "PyQt6", "PyQt6.QtCore", "PyQt6.QtGui", "PyQt6.QtWidgets"
    ]
    for module in hidden:
        cmd.append(f"--hidden-import={module}")

    # Include portable ImageMagick/Poppler
    for src, dest in extras:
        cmd.append(f"--add-data={src}{os.pathsep}{dest}")

    # Include entire src/ package so your utils/ and tabs/ are bundled
    cmd.append(f"--add-data={str(project_root/'src')}{os.pathsep}src")

    # Finally, point to the launcher script
    cmd.append(str(script))

    logging.info("Running PyInstaller: %s", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logging.error("Build failed (code %s)\nSTDOUT: %s\nSTDERR: %s",
                       result.returncode, result.stdout, result.stderr)
        sys.exit(result.returncode)
    logging.info("Build succeeded: %s/%s", dist_dir, name)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    parser = argparse.ArgumentParser(description="Build PDFManager standalone executable.")
    parser.add_argument("--icon", type=Path,
                        default=project_root / "src" / "resources" / "manage_pdf.ico",
                        help="Path to the application icon.")
    parser.add_argument("--imagick", type=Path,
                        default=project_root / "imagick_portable_64",
                        help="Directory of portable ImageMagick.")
    parser.add_argument("--poppler", type=Path,
                        default=project_root / "poppler_portable_64",
                        help="Directory of portable Poppler.")
    parser.add_argument("--workpath", type=Path, default=project_root / "build",
                        help="PyInstaller work path.")
    parser.add_argument("--distpath", type=Path, default=project_root / "dist",
                        help="PyInstaller dist path.")
    parser.add_argument("--name", default="PDFManager",
                        help="Name of the generated executable.")
    parser.add_argument("--windowed", action="store_true",
                        help="Build as a windowed (no console) application.")
    args = parser.parse_args()

    ensure_tool_installed("PyInstaller")

    extras: list[tuple[str, str]] = []
    # ImageMagick
    if args.imagick.exists() and has_executable(args.imagick, ["magick.exe", "convert.exe"]):
        extras.append((str(args.imagick), "imagick_portable_64"))
    # Poppler
    if args.poppler.exists() and has_executable(args.poppler, ["pdftoppm.exe", "pdftocairo.exe"]):
        extras.append((str(args.poppler), "poppler_portable_64"))

    # Build with our run_app launcher
    launcher = project_root / "run_app.py"
    build_executable(
        script=launcher,
        icon=args.icon,
        work_dir=args.workpath,
        dist_dir=args.distpath,
        extras=extras,
        name=args.name,
        windowed=args.windowed,
    )


