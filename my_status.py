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
    
    # Get a list of all running processes and their command lines on macOS
    running_process_cmds = []
    for proc in psutil.process_iter(['name', 'cmdline']):
        try:
            # cmdline is a list of arguments (e.g., ['wine-preloader', 'HD_Launcher.exe'])
            # We join them into a single string so we can easily search for the .exe name
            if proc.info.get('cmdline'):
                full_cmd = " ".join(proc.info['cmdline']).lower()
                running_process_cmds.append(full_cmd)
            # Fallback to process name if cmdline is restricted or empty
            elif proc.info.get('name'):
                running_process_cmds.append(proc.info['name'].lower())
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    # Find if any configured game is currently running
    matched_game = None
    for game in games:
        # This will now check if the target string (e.g., "hd_launcher.exe") is anywhere in the full command line
        proc_name = game.get("process_name", "").lower()
        if proc_name and any(proc_name in cmd for cmd in running_process_cmds):
            matched_game = game
            break

    # Case 1: A configured game started running (or switched to another game)
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
            if matched_game.get("details"):
                update_args["details"] = matched_game["details"]
            if matched_game.get("state"):
                update_args["state"] = matched_game["state"]
            if matched_game.get("large_image"):
                update_args["large_image"] = matched_game["large_image"]
            if matched_game.get("large_text"):
                update_args["large_text"] = matched_game["large_text"]

            active_rpc.update(**update_args)
            current_game = matched_game
            print(f"Detected game: {matched_game.get('game_name', matched_game['process_name'])}. Status updated!")
        except Exception as e:
            print(f"Failed to connect RPC: {e}")

    # Case 2: No configured game is running, but RPC is still connected
    elif not matched_game and active_rpc:
        try:
            active_rpc.close()
            print("Game closed. Status cleared.")
        except Exception:
            pass
        active_rpc = None
        current_game = None

    time.sleep(5)