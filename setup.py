from setuptools import setup

APP_NAME = 'Downloader'
APP = ['app.py']
DATA_FILES = ['512png.png', 'logo.png']
OPTIONS = {
    'iconfile': '512png.png',
    'argv_emulation': False,
}

setup(
    app=APP,
    name=APP_NAME,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
