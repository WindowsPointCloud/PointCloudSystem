# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['labelCloud.py'],
    pathex=[],
    binaries=[],
   datas=[
	  ('D:\\hum_final\\PointCloudSystem\\labelCloud\\labelCloud\\resources\\interfaces\\*.ui', 'resources/interfaces'),
      ('D:\\hum_final\\PointCloudSystem\\labelCloud\\labelCloud\\resources\\icons\\*.ico', 'resources/icons'),
	  ('D:\\hum_final\\PointCloudSystem\\labelCloud\\labelCloud\\resources\\icons\\*.svg', 'resources/icons'),
	   ('D:\\hum_final\\PointCloudSystem\\labelCloud\\labelCloud\\resources\\*.txt', 'resources'),
	   ('C:\\Users\\user\\anaconda3\\envs\\cuda116\\Lib\\site-packages\\cumm\\include', 'cumm/include'),
	],
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
    name='labelCloud',
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
