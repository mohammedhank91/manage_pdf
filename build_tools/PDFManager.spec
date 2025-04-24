# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['..\\src\\pdf_manage.py'],
    pathex=['..'],
    binaries=[],
    datas=[('..\\imagick_portable_64', 'imagick_portable_64'),  ('..\\src\\resources\\manage_pdf.ico', '.')],
    hiddenimports=['PIL', 'PyPDF2', 'pikepdf', 'xml', 'xml.dom'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PDFManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='..\\src\\resources\\manage_pdf.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PDFManager',
)
