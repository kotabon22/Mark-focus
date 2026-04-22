# setup.py (更新版)
from setuptools import setup

APP = ['test.py'] 
ICON_FILE = 'icon.icns' # ここを実際のファイル名にする

DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'iconfile': ICON_FILE, # アイコンを指定
    'packages': ['matplotlib', 'pandas', 'numpy', 'tkinter'],
    'includes': ['matplotlib.backends.backend_tkagg'],
    'plist': {
        'CFBundleName': 'MarkFocus',
        'CFBundleDisplayName': 'MarkFocus',
        'CFBundleIdentifier': 'com.markfocus.system',
        'CFBundleVersion': "4.0.0",
        'CFBundleShortVersionString': "4.0.0",
        'NSHighResolutionCapable': True,
    }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
