import requests
import urllib3

# Suppress the self-signed certificate warning for Riot's local API
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_rpc_update():
    """
    Queries the League of Legends Live Client Data API.
    Returns a dictionary with 'details' and 'state' to update Discord.
    """
    try:
        resp = requests.get('https://127.0.0.1:2999/liveclientdata/allgamedata', verify=False, timeout=1)
        
        if resp.status_code == 200:
            data = resp.json()
            active_name = data.get("activePlayer", {}).get("summonerName")
            
            # Find our player to check their score
            for p in data.get("allPlayers", []):
                if p.get("summonerName") == active_name:
                    scores = p.get("scores", {})
                    kills = scores.get("kills", 0)
                    deaths = scores.get("deaths", 0)
                    assists = scores.get("assists", 0)
                    
                    # Dynamic game state logic
                    if kills >= deaths + 4:
                        status = "Faker cosplay 🐐"
                    elif deaths >= kills + 4:
                        status = "Feeding 😢"
                    else:
                        status = "Not feeding 👍"
                        
                    return {
                        "details": status,
                        "state": f"KDA: {kills}/{deaths}/{assists}"
                    }
                    
    except requests.exceptions.RequestException:
        # If the API isn't available (e.g., in the client or loading screen)
        pass
        
    return {
        "details": "In Client / Loading",
        "state": "Not doing much... 🍵"
    }