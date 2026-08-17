# 🎮 MacRPC-Auto

A lightweight, native macOS Menu Bar application that lets you customize your Discord Rich Presence (RPC) based on the games or apps you're running. 

Whether you want a simple static status or a fully dynamic integration using Python plugins (like live match stats for League of Legends, the script of which is given in this repo), MacRPC-Auto handles it all silently in the background.

## ✨ Features
* **Native macOS UI:** Sits cleanly in your Menu Bar with full support for light/dark mode stencil icons.
* **Auto-Detection:** Scans your running background processes to automatically trigger your custom status.
* **Crash-Proof Background Thread:** Silently ignores macOS permission blocks and safely recovers from plugin errors without crashing.
* **Hot-Reloading:** Edit your configuration or Python plugins, and the app will instantly update your Discord status within 5 seconds—no app restart required!
* **Safe Storage:** Keeps your custom configurations safely in `~/Library/Application Support/DiscordRPC` so your settings survive future app updates.

---

## 🚀 Installation & Building

Since this is a native macOS app, you will package it yourself using `py2app`.

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR-USERNAME/MacRPC-Auto.git](https://github.com/YOUR-USERNAME/MacRPC-Auto.git)
   cd MacRPC-Auto
   ```

2. **Install the required dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```
3. **Build the macOS Application:**
   ```bash
   python3 setup.py py2app
   ```

4. **Install:**
   Drag the newly created `Discord RPC.app` from the `dist/` folder into your Mac's `Applications` folder and launch it!

---

## 🛠 How to Customize (Important!)

**⚠️ DO NOT edit the `games.json` or `plugins/` files directly in this cloned repository!** 

When you build the app, it creates a dedicated, safe folder for your live configurations. To change your custom statuses:

1. Launch the **Discord RPC** app from your Mac's Menu Bar.
2. Click **Open Config (games.json)** or **Open Plugins Folder** from the dropdown menu.
3. Edit the files that pop up on your screen and save them.
4. The app will automatically detect your changes and update Discord within 5 seconds!

### 📝 Editing `games.json` (Static Status)
To start, make your custom app in the [Discord Developer Portal](https://discord.com/developers/applications)
and add an image for it in the left sidebar (Overview -> Rich Presence -> Art Assets).

For simple games, just add an entry to your `games.json` file:
```json
[
  {
    "process_name": "minecraft",
    "client_id": "YOUR_DISCORD_APP_ID" // this is the 'Application ID' under General Information in the dev portal
    "details": "Mining diamonds",
    "state": "Singleplayer",
    "large_image": "icon_name", // this is the name of the image file you placed in Rich Presence -> Art Assets
    "large_text": "Minecraft"
  }
]
```

**🔍 Pro-Tip on Process Names:** 
macOS process names are tricky. What Activity Monitor calls "League of Legends" might actually be `leagueclient` under the hood. If your game isn't being detected, open your Terminal, run `ps -A | grep -i "your_game_name"`, and use the raw UNIX executable name in the `"process_name"` field!

---

## 🔌 Advanced: Dynamic Plugins

Want to show live in-game stats (like your current champion in League of Legends)? You can write your own Python plugins!

1. Create a Python file in your Application Support `plugins` folder (e.g., `league.py`).
2. Your script **must** contain a function called `get_rpc_update()` that returns a dictionary of Discord RPC arguments.
3. Update your `games.json` to point to the plugin instead of static text:

```json
[
  {
    "process_name": "leagueclient",
    "client_id": "YOUR_DISCORD_APP_ID",
    "plugin": "league"
  }
]
```

### Example Plugin (`league.py`):
```python
def get_rpc_update():
    # You can add logic here to fetch live data from local game APIs!
    
    return {
        "details": "Trying not to feed",
        "state": f"KDA: {kills}/{deaths}/{assists}"
    }
```
*Note: Plugins are hot-reloaded automatically. Just hit `Cmd + S` on your Python script, and your Discord status will instantly update!*

Made with Gemini(mainly) and also a little bit of Github Copilot. 

Have fun!