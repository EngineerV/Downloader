from setuptools import setup

APP_NAME = 'Downloader'
APP = ['app.py']
DATA_FILES = ['512png.png', 'logo.png']
OPTIONS = {
    'iconfile': '512png.png',
    # 'argv_emulation': True,
    'plist': {
        'CFBundleName': APP_NAME,
        'CFBundleDisplayName': APP_NAME,
        'CFBundleGetInfoString': 'Desktop Founds Control',
        'CFBundleVersion': '0.1.0 stable',
        'CFBundleShortVersionString': '0.1.0',
        'NSHumanReadableCopyRight': 'Copyright (c) 2023, VA, All Rights Reserved'
    }
}

setup(
    app=APP,
    name=APP_NAME,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
