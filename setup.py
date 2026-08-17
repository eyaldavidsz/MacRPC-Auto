from setuptools import setup

APP = ['my_status.py']
# We must explicitly tell py2app to include your config and plugins!
DATA_FILES = ['games.json', 'plugins', 'menu_iconTemplate.png'] 

OPTIONS = {
    'argv_emulation': True,
    'packages': ['rumps', 'pypresence', 'psutil', 'requests'],
    'iconfile': 'app_icon.icns',
    'plist': {
        # This is the magic macOS setting that hides the app from your Dock 
        # so it ONLY shows up in the top Menu Bar!
        'LSUIElement': True,
    },
}

setup(
    app=APP,
    name="Discord RPC",
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)