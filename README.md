# Auto Discord RPC for macOS 🍏👾

A lightweight, automated Discord Rich Presence (RPC) watcher for macOS. 

Unlike most Discord RPC tools for Mac that require you to manually click "Connect" and "Disconnect", this project uses a background Python script and a macOS Launch Agent (`launchd`) to automatically detect when your configured games open and updates your Discord status instantly. When you quit the game, it clears your status. It works perfectly with native Mac games, non-Steam games, custom executables, and launchers like GOG Galaxy, Heroic, and CrossOver!

## Features
* **Multi-Game Support:** Easily track multiple games by adding them to a simple JSON file. No need to restart the watcher when you add a new game!
* **Deep Process Scanning:** Reads full command-line arguments, meaning it perfectly detects Windows games running through Wine/CrossOver and emulators like ScummVM or DOSBox.
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

## Step 1: Installation & Setup
First, download or clone this repository to your Mac. We recommend putting it in your home folder for easy access.

Open your Terminal and run:

```bash
git clone [https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git) ~/discord-status
cd ~/discord-status
python3 -m venv venv
source venv/bin/activate
pip install pypresence psutil
```

## Step 2: Configure Your Games
This script uses a configuration file so you don't have to touch the Python code for every new game. 

Inside the `~/discord-status` folder, open `games.json` (or copy `games.example.json` to `games.json`) and add your game details:

```json
[
  {
    "game_name": "Heroes of Might and Magic III",
    "process_name": "hd_launcher.exe",
    "client_id": "YOUR_APPLICATION_ID_HERE",
    "details": "Restoring Erathia",
    "state": "In Game",
    "large_image": "homm3-cover",
    "large_text": "HoMM3 Complete"
  }
]
```

### Understanding `process_name`
Because this script scans the *entire command line argument* running on your Mac, it is incredibly flexible. Here is a quick reference for what to put in `"process_name"`:

| Game Type | What to use | Example |
| :--- | :--- | :--- |
| **Native Mac Game** | The exact name of the Mac App | `stardew valley` |
| **Wine / Heroic Game** | The name of the Windows `.exe` | `hd_launcher.exe` |
| **ScummVM/Emulators** | The unique game ID or folder name | `project-nov` |

*(See the **Troubleshooting** section below if you aren't sure how to find your game's process name!)*

## Step 3: Automating with a macOS Launch Agent
To make this run automatically in the background on startup, we use a macOS `.plist` file.

1. Open Terminal and type `whoami` to get your exact Mac username. 
2. Create the `.plist` file using nano to avoid hidden formatting issues:
```bash
nano ~/Library/LaunchAgents/com.customrp.watcher.plist
```
3. Paste the following XML code. **Replace `YOUR_USERNAME` with your actual Mac username from Step 1!**

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
5. Load the configuration into macOS to start the watcher:
```bash
launchctl load ~/Library/LaunchAgents/com.customrp.watcher.plist
```

That's it! The script is now watching for your games in the background. **To add a new game in the future, simply update your `games.json` file—the script will automatically detect the changes without needing a restart!**

---

## 🔍 How to Find Your Game's Process Name
If you are running a game through a compatibility layer like Heroic, CrossOver, or ScummVM, the process running on your Mac might not just be the name of the game. 


To find the exact `process_name` to put in your `games.json`, use this trick:

1. Launch your game so it is actively running.
2. Open your Mac's **Terminal** app.
3. Type `ps x | grep -i "something_related_to_your_game"` and hit Enter.

---

Made with the help of Gemini, Github Copilot.
