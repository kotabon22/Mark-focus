from setuptools import setup

APP = ['test.py']
DATA_FILES = []
OPTIONS = {
    # 1. ここを False にするのが最も重要です
    'argv_emulation': False, 
    
    'packages': ['tkinter'],
    # 2. 明示的に含めるモジュールを指定（csv など）
    'includes': ['tkinter', 'csv', 'os', 'datetime', 'json', 'subprocess'],
    
    'plist': {
        'CFBundleName': 'MarkFocus',
        'CFBundleDisplayName': 'MarkFocus',
        'CFBundleIdentifier': 'com.yourname.markfocus',
        'CFBundleVersion': "1.2.0",
        'CFBundleShortVersionString': "1.2.0",
        'NSHighResolutionCapable': True,
        # ダークモードでも白飛びしないための設定
        'NSRequiresAquaSystemAppearance': False,
    }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
