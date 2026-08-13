# Auto Discord RPC for macOS 🍏👾

A lightweight, automated Discord Rich Presence (RPC) watcher for macOS. Made using Gemini, Copilot.

Unlike most Discord RPC tools for Mac that require you to manually click "Connect" and "Disconnect", this project uses a background Python script and a macOS Launch Agent (`launchd`) to automatically detect when your configured games open and updates your Discord status instantly. When you quit the game, it clears your status. It works perfectly with non-Steam games, custom executables, and launchers like GOG Galaxy!

## Features
* **Multi-Game Support:** Easily track multiple games by adding them to a simple JSON file. No need to restart the watcher when you add a new game!
* **Fully Automated:** Runs invisibly in the background and updates Discord exactly when a recognized game launches.
* **No Bloatware:** Uses a simple Python script instead of a heavy, battery-draining desktop app.
* **TOS Compliant:** Uses Discord's official local IPC socket; it does **not** break Discord's Terms of Service or require account tokens.
* **Set and Forget:** Auto-starts flawlessly when you log into your Mac.

---

## Prerequisites
1. **Python 3** installed on your Mac.
2. The **Discord Desktop App** running locally.
3. A **Discord Application ID** for your game (Create a free app at the [Discord Developer Portal](https://discord.com/developers/applications)).
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

## Step 2: Configure Your Games
This script uses a configuration file so you don't have to edit the code for every new game. 

Inside the `~/discord-status` folder, create a file named `games.json` (you can copy the provided `games.example.json` file as a template). Add your game details like this:

```json
[
  {
    "game_name": "Blade Runner",
    "process_name": "Blade Runner",
    "client_id": "YOUR_APPLICATION_ID_HERE",
    "details": "Investigating Nexus-6",
    "state": "Los Angeles, 2019",
    "large_image": "blade-cover",
    "large_text": "Blade Runner"
  }
]
```
*   `process_name`: The exact name of the application process running on your Mac.
*   `large_image`: The exact name of the image you uploaded to the Discord Developer Portal.

*Note: You can add as many game blocks as you want to this list! The script will automatically detect any of them.*

## Step 3: The Python Script
Inside the `~/discord-status` folder, create a file named `my_status.py` and paste the following code:

```python
import json
import os
import time
from pypresence import Presence
import psutil

# Find the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "games.json")

def load_games():
    if not os.path.exists(CONFIG_PATH):
        return []
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading games.json: {e}")
        return []

active_rpc = None
current_game = None

print("Multi-Game Discord RPC Watcher active...")

while True:
    games = load_games()
    
    running_processes = []
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name']:
                running_processes.append(proc.info['name'].lower())
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    matched_game = None
    for game in games:
        proc_name = game.get("process_name", "").lower()
        if proc_name and any(proc_name in p for p in running_processes):
            matched_game = game
            break

    if matched_game and (matched_game != current_game):
        if active_rpc:
            try:
                active_rpc.close()
            except Exception:
                pass
            active_rpc = None

        try:
            active_rpc = Presence(matched_game["client_id"])
            active_rpc.connect()

            update_args = {}
            if matched_game.get("details"): update_args["details"] = matched_game["details"]
            if matched_game.get("state"): update_args["state"] = matched_game["state"]
            if matched_game.get("large_image"): update_args["large_image"] = matched_game["large_image"]
            if matched_game.get("large_text"): update_args["large_text"] = matched_game["large_text"]

            active_rpc.update(**update_args)
            current_game = matched_game
            print(f"Detected game: {matched_game.get('game_name', matched_game['process_name'])}. Status updated!")
        except Exception as e:
            print(f"Failed to connect RPC: {e}")

    elif not matched_game and active_rpc:
        try:
            active_rpc.close()
            print("Game closed. Status cleared.")
        except Exception:
            pass
        active_rpc = None
        current_game = None

    time.sleep(5)
```

## Step 4: Automating with a macOS Launch Agent
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

## Step 5: Start the Watcher
Load the configuration into macOS:
```bash
launchctl load ~/Library/LaunchAgents/com.customrp.watcher.plist
```

That's it! You can close Terminal. The script is now watching for your games in the background. **To add a new game in the future, simply update your `games.json` file—the script will automatically detect the changes!**

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
