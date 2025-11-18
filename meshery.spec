# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src/meshery.py'],
    pathex=[],
    binaries=[],
    datas=[('images/ogs-icon.png', 'images'), ('data/palette.gpl', 'data')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='meshery',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
app = BUNDLE(
    exe,
    name='Course Meshery.app',
    icon='images/Meshery.icns',
    bundle_identifier='com.opengolfsim.Meshery',
)
