import sys
import time
import source.gacha_bot.stations as stations
from task_manager import task_scheduler, SingletonMeta
from source.ASA.strucutres import teleporter
from source.ASA.player import player_state
from source.ASA.stations import custom_stations

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
    
    # 2. Gacha Pair 04 (tp -> gachapair04)
    stations.berry_station = False # Disable global 4-hour berry dropoff so it goes straight to pair04
    gacha4 = stations.gacha_station("gacha4", "GachaBot_gachapair04", "left")
    scheduler.add_task(gacha4)
    
    print("Test scheduler loaded! Please switch to the Ark window. Starting in 3 seconds...")
    time.sleep(3)
    scheduler.run()

if __name__ == "__main__":
    main()
