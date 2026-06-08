import sys
import time
import source.gacha_bot.stations as stations
from task_manager import task_scheduler
from source.ASA.player import player_state
from source.ASA.stations import custom_stations
import json

class dummy_render_start(stations.base_task):
    def __init__(self):
        super().__init__()
        self.name = "test_start_render"

    def execute(self):
        player_state.check_state(False)
        print("Assuming player is already standing at gachabot_render teleporter.")
        
        # Explicitly set on_tp to True since we are starting on the TP
        player_state.human.is_on_tp()
        
        from source.gacha_bot import render
        import settings
        
        render_metadata = custom_stations.get_station_metadata(settings.bed_spawn)
        render.enter_tekpod(render_metadata)
        
        from source.ASA.player import tribelog
        tribelog.open()
        time.sleep(2)

    def get_priority_level(self):
        return 1

    def get_requeue_delay(self):
        return 999999

def main():
    scheduler = task_scheduler()
    
    # 1. Start directly at render station and get into the bed
    start_task = dummy_render_start()
    scheduler.add_task(start_task)
    
    # 2. Disable global 4-hour berry dropoff so it goes straight to the pairs
    stations.state.berry_station = False 
    
    # 3. Load dynamically from gacha.json to ensure accurate data
    with open("json_files/gacha.json", "r") as f:
        gacha_data = json.load(f)
    
    for entry in gacha_data:
        name = entry["name"]
        if name in ["gacha8", "gacha7", "gacha18", "gacha17"]:
            teleporter = entry["teleporter"]
            direction = entry["side"]
            task = stations.gacha_station(name, teleporter, direction)
            scheduler.add_task(task)
            print(f"Added {name} on {teleporter} to test scheduler.")
    
    print("\nTest scheduler loaded! Please switch to the Ark window. Starting in 3 seconds...")
    time.sleep(3)
    scheduler.run()

if __name__ == "__main__":
    main()
