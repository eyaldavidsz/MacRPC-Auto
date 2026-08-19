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
The developer portal is also the only way you can change your application's *title* on Disocrd(Discord's rules don't allow you to change it dynamically as far as I know). 

For simple games, just add an entry to your `games.json` file:
```json
[
  {
    "game_name": "Minecraft", // never actually used by the code, this field serves mainly for clarity
    "process_name": "minecraft", // explanation below
    "client_id": "YOUR_DISCORD_APP_ID", // this is the 'Application ID' on the Discord dev portal(under General Info)
    "details": "Mining diamonds", // you decide what to put here
    "state": "Singleplayer(come join me!)", // you decide what to put here
    "large_image": "icon_name", // this is the name of the image file you placed in Rich Presence -> Art Assets
    "large_text": "Minecraft" // you decide what to put here, will show when you hover over the image on Discord
  }
]
```
### 🔍 Understanding `process_name`
MacRPC-Auto can detect native apps, Java games, Wine wrappers, and even specific emulator ROMs!

What Activity Monitor calls a game isn't always what the system sees. For example, Activity Monitor might show "League of Legends", but the actual background file is leagueclient. Because MacRPC-Auto checks the entire command line (which includes all the folder names), you don't have to guess the exact hidden file name. You can usually just use the game's normal title, and the script will spot it hiding in the folder path!

**If you want to make sure, here's how to find a great keyword to use for 'process_name':**
1. Make sure your game or app is currently running.
2. Open your Mac's **Terminal** app.
3. We need to see how your Mac is running the game behind the scenes. Type `ps -A | grep -i "guess"` (replace "guess" with a piece of the game's title) and hit Enter:
   `ps -A | grep -i "sims"`
4. Look at the output. You will see a long string of text showing the actual system path. 
5. Because MacRPC-Auto scans this *entire* string, you can pick **any unique keyword** from it to put in your `games.json`!

**Quick Reference Guide:**

| What you might see in Terminal (The result of your guess) | Valid keywords you could use in `games.json` |
| :--- | :--- | 
| `/Applications/Baldurs Gate 3.app/Contents/MacOS/bg3` | `baldurs gate 3` OR `bg3` | 
| `/.../CrossOver/.../The Sims 4/Game/Bin/TS4_x64.exe` | `the sims 4` OR `ts4_x64.exe` |
| `/usr/bin/java -jar /.../minecraft/versions/1.20.jar` | `minecraft` | 
| `./gogdl [...] launch /Applications/Blade Runner.app` | `blade runner` |

*Note: I don't have some of these games installed, so I used AI to generate a generic terminal output for them for the sake of the example!*

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
    # Logic here to fetch live data from local game APIs...
    
    return {
        "details": "Trying not to feed",
        "state": f"KDA: {kills}/{deaths}/{assists}"
    }
```
*Note: Plugins are hot-reloaded automatically. Just hit `Cmd + S` on your Python script, and your Discord status will instantly update!*

Made with Gemini(mainly) and also a little bit of Github Copilot. 

Have fun!