# Auto Discord RPC for macOS 🍏👾

A lightweight, native Menu Bar app for automated Discord Rich Presence (RPC) on macOS. 

Unlike most Discord RPC tools for Mac that require you to manually click "Connect" and "Disconnect" in a bulky window, this project lives quietly in your Mac's Menu Bar. It automatically detects when your configured games open and updates your Discord status instantly, clearing it when you quit. 

Powered by a modular plugin system, it can even pull live, real-time match data for supported games to dynamically update your status while you play. It works perfectly with native Mac games, non-Steam games, custom executables, and launchers like GOG Galaxy, Heroic, and CrossOver!

## Features
* **Native Menu Bar UI:** Lives discreetly in your macOS top menu bar for easy, one-click access to your configuration.
* **Multi-Game Support:** Easily track multiple games by adding them to a simple JSON file. 
* **Dynamic Plugin System:** Go beyond static text! The new plugin architecture allows the script to fetch live in-game data (like your real-time KDA in League of Legends) and instantly push it to Discord.
* **Deep Process Scanning:** Reads full command-line arguments, meaning it perfectly detects Windows games running through Wine/CrossOver and emulators like ScummVM or DOSBox.
* **No Bloatware:** Built in Python and compiled to a native Mac `.app`, avoiding heavy frameworks like Electron.
* **TOS Compliant:** Uses Discord's official local IPC socket; it does **not** break Discord's Terms of Service or require account tokens.

---

## Prerequisites
1. **Python 3** installed on your Mac.
2. The **Discord Desktop App** running locally.
3. A **Discord Application ID** for your game (Create a free app at the [Discord Developer Portal](https://discord.com/developers/applications)).
4. Uploaded artwork to your app's **Rich Presence > Art Assets** section.

---

## Step 1: Installation & Building
This app compiles directly on your machine into a standalone macOS `.app` bundle. 

Open your Terminal and run the following commands to clone the repository, install the dependencies, and build the app:

```bash
# Clone the repository
git clone [https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git) ~/discord-status
cd ~/discord-status

# Set up the virtual environment
python3 -m venv venv
source venv/bin/activate

# Install required Python libraries
pip install pypresence psutil requests rumps py2app

# Build the native macOS App bundle
python3 setup.py py2app
```

Once the build process finishes, open your Finder and navigate to the `~/discord-status/dist/` folder. Drag the newly created **Discord RPC.app** into your Mac's **Applications** folder.

## Step 2: Auto-Start (Optional but Recommended)
To make the app run seamlessly in the background when you turn on your Mac:
1. Open **System Settings > General > Login Items**.
2. Click the **+** button.
3. Select **Discord RPC.app** from your Applications folder.

---

## Step 3: Configure Your Games
To add or modify the games the app watches for, simply click the **👾 icon** in your Menu Bar and select **Open Config (games.json)**. 

Add your game details to the JSON file. You can use standard static text, or utilize a plugin for live stats:

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
  },
  {
    "game_name": "League of Legends",
    "process_name": "League of Legends",
    "client_id": "YOUR_APPLICATION_ID_HERE",
    "plugin": "league",
    "large_image": "lol-logo"
  }
]
```
*(Note: Any changes you save to this file will be automatically applied by the app within 5 seconds—no restart required!)*

### Advanced: Dynamic Plugins
If you want your Discord status to update dynamically based on live in-game events, you can assign a plugin using the `"plugin"` key (as seen in the League of Legends example above). 

*   **Included Plugins:** Currently, the `league` plugin is included out-of-the-box. It safely connects to Riot's local Live Client Data API to display your real-time Kills, Deaths, and Assists.
*   **Custom Plugins:** You can write your own game-specific logic by creating a `.py` file inside the `plugins/` directory (located by right-clicking the `.app` -> Show Package Contents -> Resources -> plugins). 

### Understanding `process_name`
Because this script scans the *entire command line argument* running on your Mac, it is incredibly flexible. Here is a quick reference for what to put in `"process_name"`:

| Game Type | What to use | Example |
| :--- | :--- | :--- |
| **Native Mac Game** | The exact name of the Mac App | `stardew valley` |
| **Wine / Heroic Game** | The name of the Windows `.exe` | `hd_launcher.exe` |
| **ScummVM/Emulators** | The unique game ID or folder name | `project-nov` |

---

## 🔍 How to Find Your Game's Process Name
If you are running a game through a compatibility layer like Heroic, CrossOver, or ScummVM, the process running on your Mac might not just be the name of the game. 

To find the exact `process_name` to put in your configuration, use this trick:

1. Launch your game so it is actively running.
2. Open your Mac's **Terminal** app.
3. Type `ps x | grep -i "something_related_to_your_game"` and hit Enter.

---

Made with the help of Gemini mainly, and Github Copilot.

Have fun!