from setuptools import setup

APP = ['Filename Assistant.py']
DATA_FILES = ['./data']
OPTIONS = {
    'iconfile':'./data/icon.icns'
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
