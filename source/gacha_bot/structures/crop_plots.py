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

def harvest_stack():
    try:
        with open("json_files/crop_plots.json", "r") as f:
            pitches = json.load(f)
    except Exception as e:
        logs.logger.error(f"Failed to load crop_plots.json: {e}")
        from source.utility.exceptions import TaskFailedException
        raise TaskFailedException("Missing or invalid crop_plots.json")

    current_crouch = False
    
    for plot in pitches:
        target_pitch = plot.get("pitch", 0)
        should_crouch = plot.get("crouched", False)
        
        if should_crouch and not current_crouch:
            player_state.human.crouch()
            current_crouch = True
        elif not should_crouch and current_crouch:
            player_state.human.reset_crouch()
            current_crouch = False
            
        utils.set_pitch(target_pitch)
        time.sleep(0.2*settings.lag_offset)
        harvest_crop()
        time.sleep(0.3*settings.lag_offset)

    #reset state back to defaults
    if current_crouch:
        player_state.human.reset_crouch()
    utils.set_pitch(0)

def harvest_3():
    #looking at the left most stack to begin with 
    harvest_stack()
    utils.turn_right(90)
    harvest_stack()
    utils.turn_right(90)
    harvest_stack()

