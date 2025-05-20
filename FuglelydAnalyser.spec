# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['analyser_lyd_main.py'], # Main script
    pathex=[], # PyInstaller usually finds paths well for CLI
    binaries=[],
    datas=[
        ('ffmpeg_macos_bin/ffmpeg', 'ffmpeg_macos_bin'), # Bundles ffmpeg into a folder named ffmpeg_macos_bin
        ('ffmpeg_macos_bin/ffprobe', 'ffmpeg_macos_bin')  # Bundles ffprobe
        # Add other non-Python data files if any
    ],
    hiddenimports=[
        'pandas._libs.tslibs.timedeltas', # Common pandas hidden import
        'tensorflow',
        'pydub',
        'soundfile',
        'requests',
        'birdnetlib',
        'scipy.special',
        'scipy.linalg',
        'librosa',
        'audioread'
        # Add others as discovered
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False, # Not relevant for macOS
    win_private_assemblies=False, # Not relevant for macOS
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='FuglelydAnalyser',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True, # Optional: can reduce size
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True, # IMPORTANT for CLI applications
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='FuglelydAnalyser',
)
# For macOS, EXE is enough. A .app bundle is not strictly necessary for a CLI tool,
# but if you want one for easier distribution or to set an icon, you can add the BUNDLE part.
# app = BUNDLE(
#     coll,
#     name='FuglelydAnalyser.app',
#     icon=None, # or 'path/to/your.icns'
#     bundle_identifier=None # e.g., 'com.yourname.fuglelydanalysercli'
# )