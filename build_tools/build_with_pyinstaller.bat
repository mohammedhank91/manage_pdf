@echo off
echo ===== PDF Manager PyInstaller Build Process =====
echo.

rem Set this to the Python executable path if needed
set PYTHON=python

echo Checking for required portable dependencies:
if exist "..\imagick_portable_64" (
    echo - ImageMagick found in imagick_portable_64
) else (
    echo - WARNING: ImageMagick not found in imagick_portable_64
)

if exist "..\poppler_portable_64" (
    echo - Poppler found in poppler_portable_64
) else (
    echo - WARNING: Poppler not found in poppler_portable_64
)

echo.
echo Step 1: Building executable with PyInstaller
%PYTHON% build_tools/build_with_pyinstaller.py
if %ERRORLEVEL% NEQ 0 (
    echo Error building executable with PyInstaller
    exit /b %ERRORLEVEL%
)

echo.
echo Step 2: Creating installer with InnoSetup
echo.

rem Check for InnoSetup compiler
set ISCC_PATH=
for %%X in (iscc.exe) do (set ISCC_PATH=%%~$PATH:X)
if defined ISCC_PATH (
    echo Found InnoSetup compiler at: %ISCC_PATH%
) else (
    echo ERROR: InnoSetup compiler (iscc.exe) not found in PATH
    echo Please install InnoSetup from https://jrsoftware.org/isdl.php
    echo and add it to your PATH environment variable
    exit /b 1
)

echo Running InnoSetup compiler...
iscc "build_tools\PDFManager_PyInstaller_Setup.iss"
if %ERRORLEVEL% NEQ 0 (
    echo Error creating installer
    exit /b %ERRORLEVEL%
)

echo.
echo ===== Build completed successfully! =====
echo Installer created in installer_64 directory
echo. 