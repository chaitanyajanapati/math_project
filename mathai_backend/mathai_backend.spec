# PyInstaller spec for MathAI Backend
# This script bundles your FastAPI backend as a Windows executable.
# Usage: pyinstaller mathai_backend.spec

block_cipher = None

import sys
import os
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Main entry point
main_script = os.path.join('mathai_backend', 'main.py')

# Collect all Python modules from model and backend folders
hiddenimports = collect_submodules('mathai_ai_models') + collect_submodules('app')

datas = []
# Include data files (JSON, YAML, etc.)
datas += collect_data_files('mathai_backend/app/data')
datas += collect_data_files('mathai_ai_models')
# Include ollama config if needed
datas += [(os.path.join('mathai_ai_models', 'ollama_config.yaml'), 'mathai_ai_models')]

# If you use other config/data files, add them here

from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT

a = Analysis([
    main_script
],
    pathex=[os.getcwd()],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='mathai_backend',
          debug=False,
          strip=False,
          upx=True,
          console=True)
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='mathai_backend')
