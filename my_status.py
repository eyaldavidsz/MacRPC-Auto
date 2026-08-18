import json
import os
import sys
import time
import psutil
import importlib
import threading
import subprocess
import shutil
import rumps
import importlib.util
from pypresence import Presence

# --- 1. PATH SETUP ---
if 'RESOURCEPATH' in os.environ:
    BUNDLE_DIR = os.environ['RESOURCEPATH']
else:
    BUNDLE_DIR = os.path.dirname(os.path.realpath(__file__))

# Define the user's Application Support folder
APP_SUPPORT_DIR = os.path.expanduser("~/Library/Application Support/DiscordRPC")
CONFIG_PATH = os.path.join(APP_SUPPORT_DIR, "games.json")
PLUGINS_DIR = os.path.join(APP_SUPPORT_DIR, "plugins")

# Create the Application Support folder if it doesn't exist
os.makedirs(APP_SUPPORT_DIR, exist_ok=True)

# Copy the default games.json on first launch
if not os.path.exists(CONFIG_PATH):
    default_config = os.path.join(BUNDLE_DIR, "games.json")
    if os.path.exists(default_config):
        shutil.copy(default_config, CONFIG_PATH)

# Copy the default plugins folder on first launch
if not os.path.exists(PLUGINS_DIR):
    default_plugins = os.path.join(BUNDLE_DIR, "plugins")
    if os.path.exists(default_plugins):
        shutil.copytree(default_plugins, PLUGINS_DIR)

# Point Python's compass to the new Application Support folder so it finds the live plugins
sys.path.insert(0, APP_SUPPORT_DIR)

# --- 2. BACKGROUND RPC LOGIC ---
def get_running_games():
    """Reads the JSON config and checks if any configured games are currently running."""
    try:
        with open(CONFIG_PATH, "r") as f:
            games = json.load(f)
    except Exception as e:
        return None

    # 1. Grab the full command line of every running app
    running_cmdlines = []
    for p in psutil.process_iter(['cmdline']):
        try:
            cmd = p.info.get('cmdline')
            if cmd:
                # 2. Glue the list together into one giant lowercase sentence
                full_cmd_string = " ".join(cmd).lower()
                running_cmdlines.append(full_cmd_string)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    # 3. Check our cheat sheet against the command lines
    for game in games:
        target_name = game.get("process_name", "").lower()
        
        # Look through every massive command line string running on the Mac
        for running_cmd in running_cmdlines:
            # If your custom process_name appears ANYWHERE in that string, it's a match!
            if target_name in running_cmd:
                return game
                
    return None

def update_rpc():
    """The background loop that updates Discord."""
    rpc = None
    current_client_id = None

    while True:
        # THE MASTER SAFETY NET:
        # This try/except block ensures that if absolutely anything goes wrong,
        # the thread will sleep for 5 seconds and try again, instead of dying.
        try:
            active_game = get_running_games()

            if active_game:
                client_id = active_game.get("client_id")
                
                # Connect to Discord RPC if we aren't already connected
                if rpc is None or current_client_id != client_id:
                    if rpc:
                        rpc.close()
                    try:
                        rpc = Presence(client_id)
                        rpc.connect()
                        current_client_id = client_id
                    except Exception:
                        rpc = None

                if rpc:
                    # If the game uses a dynamic plugin
                    if "plugin" in active_game:
                        plugin_name = active_game["plugin"]
                        plugin_path = os.path.join(PLUGINS_DIR, f"{plugin_name}.py")
                        
                        try:
                            # Direct file loading from the Application Support folder
                            spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
                            plugin_module = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(plugin_module)
                            
                            plugin_data = plugin_module.get_rpc_update() 
                            
                            if plugin_data:
                                rpc.update(**plugin_data)
                                
                        except Exception as plugin_error:
                            error_log_path = os.path.join(APP_SUPPORT_DIR, "error_log.txt")
                            with open(error_log_path, "a") as f:
                                f.write(f"[{time.ctime()}] Plugin error: {plugin_error}\n")
                    
                    # If it's a standard static game config
                    else:
                        rpc.update(
                            state=active_game.get("state"),
                            details=active_game.get("details"),
                            large_image=active_game.get("large_image"),
                            large_text=active_game.get("large_text")
                        )

            else:
                # No game running, disconnect RPC
                if rpc:
                    try:
                        rpc.close()
                    except:
                        pass
                    rpc = None
                    current_client_id = None

        except Exception as main_thread_error:
            # If the background thread hits a critical error, log it!
            error_log_path = os.path.join(APP_SUPPORT_DIR, "error_log.txt")
            with open(error_log_path, "a") as f:
                f.write(f"[{time.ctime()}] Critical Thread Error: {main_thread_error}\n")
        
        # Always wait 5 seconds before checking again
        time.sleep(5)

# --- 3. MENU BAR UI ---
class DiscordRPCApp(rumps.App):
    def __init__(self):
        # We load the icon directly from the internal bundle, not the application support folder
        icon_path = os.path.join(BUNDLE_DIR, "menu_iconTemplate.png")
        
        super(DiscordRPCApp, self).__init__(
            "Discord RPC", 
            title="", 
            icon=icon_path, 
            template=True # Forces macOS to use the stencil mode for light/dark theme matching
        )

    @rumps.clicked("Open Config (games.json)")
    def open_config(self, _):
        # Opens the user-editable config in the Application Support folder
        subprocess.call(["open", CONFIG_PATH])

    @rumps.clicked("Open Plugins Folder")
    def open_plugins(self, _):
        # Opens the user-editable plugins in the Application Support folder
        subprocess.call(["open", PLUGINS_DIR])


if __name__ == "__main__":
    # Start the background Discord loop in a separate daemon thread
    threading.Thread(target=update_rpc, daemon=True).start()
    
    # Run the native macOS menu bar UI
    DiscordRPCApp().run()