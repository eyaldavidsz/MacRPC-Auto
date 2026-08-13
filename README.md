# Auto Discord RPC for macOS 🍏👾

Made with Gemini and Copilot.

A lightweight, automated Discord Rich Presence (RPC) watcher for macOS. 

Unlike most Discord RPC tools for Mac that require you to manually click "Connect" and "Disconnect" every time you play, this project uses a background Python script and a macOS Launch Agent (`launchd`) to automatically detect when a specific game opens and updates your Discord status instantly. When you quit the game, it clears your status. It works perfectly with non-Steam games, custom executables, and launchers like GOG Galaxy!

## Features
* **Fully Automated:** Runs invisibly in the background and updates Discord exactly when your game launches.
* **No Bloatware:** Uses a simple Python script instead of a heavy, battery-draining desktop app.
* **TOS Compliant:** Uses Discord's official local IPC socket; it does **not** break Discord's Terms of Service or require account tokens.
* **Set and Forget:** Auto-starts flawlessly when you log into your Mac.

---

## Prerequisites
1. **Python 3** installed on your Mac.
2. The **Discord Desktop App** running locally.
3. A **Discord Application ID** (Create a free app at the [Discord Developer Portal](https://discord.com/developers/applications)).
4. Uploaded artwork to your app's **Rich Presence > Art Assets** section.

---

## Step 1: Setting up the Environment
Open your Terminal and create a dedicated folder and virtual environment for the script:

```bash
mkdir ~/discord-status
cd ~/discord-status
python3 -m venv venv
source venv/bin/activate
```

Install the required Python libraries (`pypresence` to talk to Discord, and `psutil` to scan for open games):

```bash
pip install pypresence psutil
```

## Step 2: The Python Script
Inside the `~/discord-status` folder, create a file named `my_status.py` and paste the following code. 

**Make sure to edit the `client_id`, `game_process_name`, and the `RPC.update` strings to match your specific game and artwork!**

```python
import time
from pypresence import Presence
import psutil

client_id = "YOUR_APP_ID_HERE"
game_process_name = "Blade Runner"  # Change this to the exact name of your application

RPC = None
is_connected = False

def is_game_running():
    for proc in psutil.process_iter(['name']):
        try:
            if game_process_name.lower() in proc.info['name'].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

print(f"Watching for {game_process_name}...")

while True:
    game_running = is_game_running()

    if game_running and not is_connected:
        try:
            RPC = Presence(client_id)
            RPC.connect()
            RPC.update(
                details="Investigating Nexus-6",     # Top line of text
                state="Los Angeles, 2019",           # Bottom line of text
                large_image="blade-cover",           # Name of your uploaded Art Asset
                large_text="Blade Runner"
            )
            is_connected = True
            print("Game detected! Status updated.")
        except Exception as e:
            pass

    elif not game_running and is_connected:
        try:
            RPC.close()
            is_connected = False
            print("Game closed. Status cleared.")
        except Exception as e:
            pass

    time.sleep(5)
```

## Step 3: Automating with a macOS Launch Agent
To make this run automatically in the background on startup, we use a macOS `.plist` file.

1. Open Terminal and type `whoami` to get your exact Mac username. 
2. Create the `.plist` file using nano to avoid hidden formatting issues:
```bash
nano ~/Library/LaunchAgents/com.customrp.watcher.plist
```
3. Paste the following XML code. **Replace `YOUR_USERNAME` with your actual Mac username!**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "[http://www.apple.com/DTDs/PropertyList-1.0.dtd](http://www.apple.com/DTDs/PropertyList-1.0.dtd)">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.customrp.watcher</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/Users/YOUR_USERNAME/discord-status/venv/bin/python3</string>
        <string>/Users/YOUR_USERNAME/discord-status/my_status.py</string>
    </array>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```
4. Save and exit (`Ctrl + O`, `Enter`, `Ctrl + X`).

## Step 4: Start the Watcher
Load the configuration into macOS:
```bash
launchctl load ~/Library/LaunchAgents/com.customrp.watcher.plist
```

That's it! You can close Terminal. The script is now watching for your game in the background.

---

## Troubleshooting

### I got `Load failed: 5: Input/output error` when loading the `.plist`!
This usually means a version of the script is already loaded and stuck, or the file has invalid formatting (often caused by using Mac's default TextEdit app which adds "smart quotes"). 

**To check for formatting errors:**
```bash
plutil -lint ~/Library/LaunchAgents/com.customrp.watcher.plist
```
If it says `OK`, your formatting is fine. You just need to clear the stuck process.

**To fix the error and reload:**
```bash
launchctl unload ~/Library/LaunchAgents/com.customrp.watcher.plist
launchctl load ~/Library/LaunchAgents/com.customrp.watcher.plist
```
If you get no output after the `load` command, it successfully loaded!

### Stopping the Script
If you ever want to permanently stop the watcher from running in the background, run:
```bash
launchctl unload ~/Library/LaunchAgents/com.customrp.watcher.plist
```
