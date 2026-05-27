import time 
import settings
from source.utility import utils ,template , windows ,variables ,screen ,local_player
from source.logs import gachalogs as logs
from source.ASA.strucutres import teleporter , inventory
from source.ASA.stations import custom_stations
from source.ASA.player import player_inventory , player_state
import source.gacha_bot.config 

def pego_pickup(metadata):
    # First, let's try the exact configured pitch in case it works
    utils.set_pitch(metadata.pitch)
    time.sleep(0.2*settings.lag_offset)
    
    utils.press_key("AccessInventory")
    time.sleep(0.5)
    
    # If not open, start sweeping
    if not template.check_template("inventory", 0.7):
        logs.logger.warning("Failed to open Pego at exact pitch. Starting vertical sweep search...")
        # Reset to looking straight ahead to start the sweep
        utils.set_pitch(0)
        time.sleep(0.2)
        
        found = False
        for sweep in range(25): # Sweep down 25 times (75 degrees total)
            utils.turn_down(3) 
            utils.press_key("AccessInventory")
            time.sleep(0.4) # Wait briefly for inventory UI to appear
            if template.check_template("inventory", 0.7):
                logs.logger.info(f"Found Pego inventory during sweep at step {sweep}!")
                found = True
                break
                
        if not found:
            logs.logger.error(f"the pego at {metadata.name} could not be found during sweep search")
            from source.utility.exceptions import TaskFailedException
            raise TaskFailedException("Failed to find Pego during vertical sweep")

    if inventory.is_open():# prevents pego being FLUNG
        player_inventory.drop_all_inv()
        time.sleep(0.2*settings.lag_offset)
        inventory.transfer_all_from()
        time.sleep(0.2*settings.lag_offset)
        inventory.close() 
        
    time.sleep(0.1*settings.lag_offset)
    utils.turn_down(utils.current_pitch)
    time.sleep(0.1*settings.lag_offset)
        