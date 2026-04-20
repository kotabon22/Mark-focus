from setuptools import setup

APP = ['test.py']  # あなたのファイル名
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'icon.icns',  # ←ここを追加！
    'packages': ['matplotlib', 'tkinter', 'pandas'],
    'includes': ['matplotlib.backends.backend_tkagg'],
    'plist': {
        'CFBundleName': 'MarkFocus',
        'CFBundleDisplayName': 'MarkFocus',
        'CFBundleIdentifier': 'com.markfocus.system',
        'CFBundleVersion': "2.9",
        'CFBundleShortVersionString': "2.9",
    }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
