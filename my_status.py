
    
    
    
    
    
    
    
    
import time
from pypresence import Presence
import psutil

client_id = "1537568478268227796"
game_process_name = "Blade Runner"  # The exact name of the application

RPC = None
is_connected = False

def is_game_running():
    # Scan running processes on your Mac
    for proc in psutil.process_iter(['name']):
        try:
            if game_process_name.lower() in proc.info['name'].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

print("Watching for Blade Runner...")

while True:
    game_running = is_game_running()

    # The game just opened!
    if game_running and not is_connected:
        try:
            RPC = Presence(client_id)
            RPC.connect()
            RPC.update(
                large_image="blade-cover",
                large_text="Blade Runner"
            )
            is_connected = True
            print("Game detected! Status updated.")
        except Exception as e:
            pass

    # The game just closed!
    elif not game_running and is_connected:
        try:
            RPC.close()
            is_connected = False
            print("Game closed. Status cleared.")
        except Exception as e:
            pass

    # Check again every 5 seconds
    time.sleep(5)