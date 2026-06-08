from source.utility import utils ,template , windows ,variables ,screen ,local_player
from source.logs import gachalogs as logs
from source.ASA.player import player_state , tribelog 
from source.ASA.strucutres import bed
import time 
import settings
import source.ASA.config 
import source.ASA.stations.custom_stations


def is_open():
    return template.check_template("teleporter_title",0.7)
    
def open():
    """
    player should already be looking down at the teleporter this just opens and WILL try and correct if there are issues 
    """
    attempts = 0
    while not is_open():
        attempts += 1
        utils.press_key("Use")
    
        if not template.template_await_true(template.check_template,2,"teleporter_title",0.7):
            logs.logger.warning("teleporter didnt open retrying now")
            player_state.check_state(False)
            # check state of char which should close out of any windows we are in or rejoin the game
            utils.pitch_zero() # reseting the chars pitch/yaw
            utils.turn_down(89)
            time.sleep(0.2*settings.lag_offset) 
        
        if attempts >= source.ASA.config.teleporter_open_attempts:
            logs.logger.error(f"unable to open up the teleporter after {source.ASA.config.teleporter_open_attempts} attempts")
            bed.spawn_in(settings.bed_spawn)
            time.sleep(20)
            utils.pitch_zero() # reseting the chars pitch/yaw
            utils.turn_down(89)
            time.sleep(5)
            break
        
def close():
    attempts = 0
    while is_open():
        attempts += 1
        logs.logger.debug(f"trying to close the teleporter {attempts} / {source.ASA.config.teleporter_close_attempts}")
        windows.click(variables.get_pixel_loc("back_button_tp_x"),variables.get_pixel_loc("back_button_tp_y"))
        time.sleep(0.2*settings.lag_offset)

        if attempts >= source.ASA.config.teleporter_close_attempts:
            logs.logger.error(f"unable to close the teleporter after {source.ASA.config.teleporter_close_attempts} attempts")
            break
    
def teleport_not_default(arg):
    if player_state.human.on_tp == False:
        time.sleep(0.2*settings.lag_offset)
        utils.turn_down(89)
        time.sleep(0.3*settings.lag_offset)
        bed.fast_travel(settings.bed_spawn) # spawns on render bed which is on the tp
        time.sleep(0.2*settings.lag_offset)
        
    if isinstance(arg, source.ASA.stations.custom_stations.station_metadata):
        stationdata = arg
    else:
        stationdata = source.ASA.stations.custom_stations.get_station_metadata(arg)
    
    teleporter_name = stationdata.name
    time.sleep(0.3*settings.lag_offset)
    utils.turn_down(89)
    time.sleep(0.3*settings.lag_offset)
    for retry_attempts in range(3):
        open() 
        time.sleep(0.2*settings.lag_offset) #waiting for teleport_icon to populate on the screen before we check
        if is_open():
            player_state.human.is_on_tp()
            if template.teleport_icon(0.55):
                start = time.time()
                logs.logger.debug(f"teleport icons are not on the teleport screen waiting for up to 10 seconds for them to appear")
                template.template_await_true(template.teleport_icon,10,0.55)
                logs.logger.debug(f"time taken for teleporter icon to appear : {time.time() - start}")
            time.sleep(1.0 * settings.lag_offset) # Let the UI fully settle before trying to type
            counter = 0
            while template.check_template_no_bounds("search",0.7):
                counter += 1
                windows.click(variables.get_pixel_loc("search_bar_tp_x"),variables.get_pixel_loc("search_bar_tp_y"))
                time.sleep(0.5 * settings.lag_offset) # Wait for focus
                utils.ctrl_a()
                time.sleep(0.2 * settings.lag_offset)
                utils.write(teleporter_name)
                time.sleep(1.0 * settings.lag_offset) # Give the game time to process the text input and remove the "Search" placeholder!
                if counter >= 3:
                    logs.logger.error(f"search still detected likely did not type anything")
                    break
                    
            # Wait extra time for the filtered list to populate before blindly clicking the top slot!
            time.sleep(0.5 * settings.lag_offset)
            windows.click(variables.get_pixel_loc("first_bed_slot_x"),variables.get_pixel_loc("first_bed_slot_y"))
            time.sleep(0.3*settings.lag_offset) #preventing the orange text from the starting teleport screen messing things up
            if not template.template_await_true(template.check_teleporter_orange,3):
                logs.logger.warning(f"orange pixel for teleporter ready not found likely already on the tp we are just exiting the tp treating it as the tp we should be on")
                close() # closing out as either the TP couldnt be found however we still want to change to the station yaw so we still continue
                break # Treat as success (already there)
            else:
                time.sleep(0.2*settings.lag_offset)
                windows.click(variables.get_pixel_loc("first_bed_slot_x"),variables.get_pixel_loc("first_bed_slot_y"))
                time.sleep(0.2*settings.lag_offset)
                windows.click(variables.get_pixel_loc("spawn_button_x"),variables.get_pixel_loc("spawn_button_y"))

                if template.template_await_true(template.white_flash,2):
                    logs.logger.debug(f"white flash detected waiting for up too 5 seconds")
                    template.template_await_false(template.white_flash,5)
                
                time.sleep(1.5 * settings.lag_offset) # Wait for teleport to process
                
                if is_open():
                    logs.logger.warning(f"Teleporter is still open after attempt {retry_attempts + 1}. Retrying...")
                    close()
                    time.sleep(1.0 * settings.lag_offset)
                    utils.turn_down(89)
                    time.sleep(0.3 * settings.lag_offset)
                    continue # Retry the loop!
                
                # If we made it here, we successfully teleported!
                tribelog.open() 
                tribelog.close()
                break # Break out of the retry loop
        else:
            logs.logger.warning("Teleporter did not open successfully.")
            
    if is_open():
        logs.logger.error("Failed to teleport after 3 attempts. Throwing exception to trigger death recovery.")
        from source.utility.exceptions import TaskFailedException
        raise TaskFailedException("Stuck on teleporter screen")

    time.sleep(0.5*settings.lag_offset)
    if settings.singleplayer: # single player for some reason changes view angles when you tp 
        utils.current_pitch = 0
        utils.turn_down(89)
        time.sleep(0.2)
        
    utils.set_yaw(stationdata.yaw)
        
            


                
                              

                
                