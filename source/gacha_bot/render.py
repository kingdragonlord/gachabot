import time 
import settings
from source.utility import utils ,template , windows ,variables ,screen ,local_player
from source.logs import gachalogs as logs
from source.ASA.strucutres import teleporter , inventory
from source.ASA.stations import custom_stations
from source.ASA.player import player_inventory , player_state , buffs
import source.gacha_bot.config 
import pyautogui

render_flag = False #starts as false as obviously we are not rendering anything

def is_open():
    return template.check_template_no_bounds("bed_radical",0.6)

def enter_tekpod(metadata=None):
    global render_flag
    attempts = 0 
    while not render_flag:
        attempts += 1
        if attempts == source.gacha_bot.config.render_attempts:
            logs.logger.warning(f"{attempts} attempts however bot could not get into the render bed we are dieing and respawning to try and fix this")
            player_inventory.implant_eat()
            player_state.check_state() # this should respawn our char in the bed
            
        time.sleep(0.5*settings.lag_offset)    
        utils.press_key("Run") #uncrouching char just in case
        
        # Determine sweep offsets to combat player drift
        sweep_yaw = 0
        sweep_pitch = 0
        if attempts == 2: sweep_yaw = 5
        elif attempts == 3: sweep_yaw = -5
        elif attempts == 4: sweep_yaw = 10
        elif attempts == 5: sweep_yaw = -10
        elif attempts == 6: sweep_pitch = 5
        elif attempts == 7: sweep_pitch = -5
        elif attempts == 8: sweep_yaw = 5; sweep_pitch = 5
        elif attempts == 9: sweep_yaw = -5; sweep_pitch = 5
        
        if sweep_yaw != 0 or sweep_pitch != 0:
            logs.logger.info(f"Sweep attempt {attempts}: Offset Yaw by {sweep_yaw}, Pitch by {sweep_pitch}")
        
        if metadata and getattr(metadata, "yaw", None) is not None and getattr(metadata, "yaw") != 0.0:
            utils.set_yaw(metadata.yaw + sweep_yaw)
            utils.set_pitch(metadata.pitch + sweep_pitch)
        else:
            utils.zero()
            utils.set_yaw(settings.station_yaw + sweep_yaw)
            utils.turn_down(15 - sweep_pitch) # Note: turn_down subtracts from pitch mentally, so minus
            
        time.sleep(0.3*settings.lag_offset)
        utils.key_down("Use")
        time.sleep(0.5*settings.lag_offset)

        if template.template_await_true(template.check_template_no_bounds,1,"bed_radical",0.6):
            time.sleep(0.2*settings.lag_offset)
            windows.move_mouse(variables.get_pixel_loc("radical_laydown_x"), variables.get_pixel_loc("radical_laydown_y"))
            time.sleep(0.5*settings.lag_offset)
            utils.key_up("Use")
            time.sleep(4 * settings.lag_offset)
            
            # Since the infinite loop was fixed, we assume success if we clicked the radical menu
            logs.logger.critical(f"bot successfully clicked the radial menu to enter the bed on attempt {attempts}")
            render_flag = True
            utils.current_pitch = 0 
            break
            
        else:
            # Bed radical not found, release Use key and loop back for next sweep attempt
            utils.key_up("Use")
            time.sleep(0.5*settings.lag_offset)    
            if attempts == 2:
                logs.logger.warning(f"failed to enter tekpod moving character around before retrying")
                utils.press_key("Run")
        
        if attempts >= source.gacha_bot.config.render_attempts:
            logs.logger.error(f"we were unable to get into the tekpod after {attempts} attempts pausing execution to avoid unbreakable loops")
            break

def leave_tekpod():
    global render_flag
    player_state.reset_state() 
    time.sleep(2.0*settings.lag_offset) # Increased delay to ensure Ark accepts the 'Use' command
    utils.press_key(local_player.get_input_settings("Use"))
    
    logs.logger.debug("waiting for tekpod exit animation to complete")
    time.sleep(4.5 * settings.lag_offset)
    
    if template.check_buffs("tek_pod_buff", 0.7):
        logs.logger.warning("bot didnt leave the tekpod first try we are retrying now")
        utils.press_key(local_player.get_input_settings("Use"))
        time.sleep(4.5 * settings.lag_offset)
        
    render_flag = False

def fast_travel_to_render():
    if render_flag:
        #we need to leave tekpod and look at it 
        leave_tekpod()
        return
    if player_state.human.on_tp:
        #we need to tp to render tp
        teleporter.teleport_not_default(settings.bed_spawn)
        

