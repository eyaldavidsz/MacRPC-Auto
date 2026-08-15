import json
import os
import time
import psutil
import importlib
from pypresence import Presence

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
last_game_state_hash = None 

print("Multi-Game Discord RPC Watcher active (Plugin System Enabled)...")

while True:
    games = load_games()
    
    running_process_cmds = []
    for proc in psutil.process_iter(['name', 'cmdline']):
        try:
            if proc.info.get('cmdline'):
                full_cmd = " ".join(proc.info['cmdline']).lower()
                running_process_cmds.append(full_cmd)
            elif proc.info.get('name'):
                running_process_cmds.append(proc.info['name'].lower())
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    matched_game = None
    for game in games:
        proc_name = game.get("process_name", "").lower()
        if proc_name and any(proc_name in cmd for cmd in running_process_cmds):
            matched_game = game
            break

    # Case 1: A configured game is running
    if matched_game:
        # 1. Start with default details from games.json
        current_details = matched_game.get("details")
        current_state = matched_game.get("state")

        # 2. Check if the game has a custom plugin assigned
        plugin_name = matched_game.get("plugin")
        if plugin_name:
            try:
                # Dynamically load plugins/league.py (or any other plugin)
                plugin_module = importlib.import_module(f"plugins.{plugin_name}")
                plugin_data = plugin_module.get_rpc_update()
                
                # Override the default JSON text with the dynamic plugin text
                if plugin_data:
                    current_details = plugin_data.get("details", current_details)
                    current_state = plugin_data.get("state", current_state)
            except Exception as e:
                print(f"Error running plugin '{plugin_name}': {e}")

        # 3. Create a unique hash to check if we actually need to update Discord
        current_game_state_hash = f"{matched_game.get('client_id')}_{current_details}_{current_state}"

        # 4. Push the update if it's a NEW game, OR if our dynamic plugin stats changed
        if (matched_game != current_game) or (current_game_state_hash != last_game_state_hash):
            
            if matched_game != current_game:
                if active_rpc:
                    try:
                        active_rpc.close()
                    except Exception:
                        pass
                
                try:
                    active_rpc = Presence(matched_game["client_id"])
                    active_rpc.connect()
                except Exception as e:
                    print(f"Failed to connect RPC: {e}")
                    active_rpc = None

            if active_rpc:
                update_args = {}
                if current_details: update_args["details"] = current_details
                if current_state: update_args["state"] = current_state
                if matched_game.get("large_image"): update_args["large_image"] = matched_game["large_image"]
                if matched_game.get("large_text"): update_args["large_text"] = matched_game["large_text"]

                try:
                    active_rpc.update(**update_args)
                    current_game = matched_game
                    last_game_state_hash = current_game_state_hash
                    print(f"[{time.strftime('%H:%M:%S')}] Status Updated: {current_details} | {current_state}")
                except Exception as e:
                    print(f"Failed to push update to Discord: {e}")

    # Case 2: No configured game is running, clear status
    elif not matched_game and active_rpc:
        try:
            active_rpc.close()
            print("Game closed. Status cleared.")
        except Exception:
            pass
        active_rpc = None
        current_game = None
        last_game_state_hash = None

    time.sleep(5)