import time 
import settings
import json
from source.utility import utils ,template , windows ,variables ,screen ,local_player
from source.logs import gachalogs as logs
from source.ASA.strucutres import teleporter , inventory , indi_forge
from source.ASA.stations import custom_stations
from source.ASA.player import player_inventory , player_state
import source.gacha_bot.config 
import source.ASA.inventories.structures


def harvest_crop():
    inventory.open()
    inventory.search_in_object("trap") #get y traps out of crop plot
    inventory.transfer_all_from()
    player_inventory.transfer_all_inventory() #transfer all the snow pellets into the crop plot
    inventory.close()

def harvest_stack(side):
    file_name = f"json_files/ytrap_{side}_plots.json"
    try:
        with open(file_name, "r") as f:
            plots = json.load(f)
    except Exception as e:
        logs.logger.error(f"Failed to load {file_name}: {e}")
        from source.utility.exceptions import TaskFailedException
        raise TaskFailedException(f"Missing or invalid {file_name}")

    current_crouch = False
    
    for plot in plots:
        target_pitch = plot.get("pitch", 0)
        target_yaw = plot.get("yaw", None)
        should_crouch = plot.get("crouched", False)
        
        # 1. Aim first. If we are currently crouched and we need to aim with ccc, explicitly uncrouch FIRST!
        # ccc forces a stand-up, which plays an animation that blocks further crouch inputs if we don't wait.
        if target_yaw is not None:
            if current_crouch:
                player_state.human.reset_crouch()
                current_crouch = False
                time.sleep(1.5 * settings.lag_offset) # Let the stand-up animation finish
            
            utils.set_yaw(target_yaw)
            current_crouch = False # Just in case
            utils.set_pitch(target_pitch)
        else:
            utils.set_pitch(target_pitch)
            
        # 2. Apply crouching if needed
        if should_crouch and not current_crouch:
            player_state.human.crouch()
            current_crouch = True
        elif not should_crouch and current_crouch:
            player_state.human.reset_crouch()
            current_crouch = False
            
        time.sleep(0.2*settings.lag_offset)
        harvest_crop()
        time.sleep(0.3*settings.lag_offset)

    #reset state back to defaults
    if current_crouch:
        player_state.human.reset_crouch()
    utils.set_pitch(0)

