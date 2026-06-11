import time 
import settings
from source.utility import utils ,template , windows ,variables ,screen ,local_player
from source.logs import gachalogs as logs
from source.ASA.strucutres import teleporter , inventory
from source.ASA.stations import custom_stations
from source.ASA.player import player_inventory , player_state ,console
import source.gacha_bot.config 
import source.gacha_bot.structures.crop_plots as crop_plots

def clean_and_feed_gacha():
    if inventory.is_open():
        logs.logger.debug("Executing clean and feed sequence for Gacha")
        inventory.transfer_all_from()
        
        player_inventory.search_in_inventory("trap")
        time.sleep(0.2*settings.lag_offset)
        player_inventory.transfer_all_inventory()
        
        player_inventory.search_in_inventory("seed")
        time.sleep(0.2*settings.lag_offset)
        player_inventory.transfer_all_inventory()
        
        player_inventory.search_in_inventory("pell")
        time.sleep(0.2*settings.lag_offset)
        player_inventory.transfer_all_inventory()
        
        player_inventory.popcorn_inventory()

def check_drift():
    import math
    from source.ASA.player import player_state
    
    ccc_data = utils.zero()
    if ccc_data and len(ccc_data) >= 2:
        try:
            curr_x = float(ccc_data[0])
            curr_y = float(ccc_data[1])
            if player_state.human.anchor_x is None:
                player_state.human.anchor_x = curr_x
                player_state.human.anchor_y = curr_y
                logs.logger.info(f"Anchored position at {curr_x}, {curr_y}")
            else:
                distance = math.sqrt((curr_x - player_state.human.anchor_x)**2 + (curr_y - player_state.human.anchor_y)**2)
                if distance > 50:
                    logs.logger.warning(f"DRIFT DETECTED! Moved {distance:.2f} units from anchor. Triggering realign.")
                    return "DRIFT_DETECTED"
        except Exception as e:
            logs.logger.error(f"Error during drift detection: {e}")
    return "OK"

def drop_off(metadata): #drop off for 150 stacks of seeds
    if check_drift() == "DRIFT_DETECTED":
        return "DRIFT_DETECTED"

    direction = metadata.side
    if direction == "right":
        turn_constant = 1
    else:
        turn_constant = -1

    utils.turn_right(40*turn_constant)
    time.sleep(0.2*settings.lag_offset)
    inventory.open()
    temp = False
    if inventory.is_open():
        inventory.transfer_all_from()
        if template.template_await_true(template.check_template_no_bounds,1,"slot_capped",0.7):
            logs.logger.debug(f"player is overcapped")
            inventory.drop_all_obj() # as our player is overcapped the gacha will also be overcapped + we have seeds in our inventory which is more important than pellets
            player_inventory.search_in_inventory("pell")
            if not template.template_await_true(template.check_template_no_bounds,0.5,"snow_owl_pellet",0.5):
                logs.logger.warning(f"GACHA is full of seeds") #warning the gacha is full of seeds as obviously something is wrong 
                player_inventory.close()
                time.sleep(0.1*settings.lag_offset)
                utils.turn_right(180)
                time.sleep(0.1*settings.lag_offset)
                player_inventory.open()
                player_inventory.search_in_inventory("seed")
                temp = True
            windows.click(variables.get_pixel_loc("inv_slot_start_x")+50,variables.get_pixel_loc("inv_slot_start_y")+70)
            for x in range(8):
                windows.move_mouse(variables.get_pixel_loc("inv_slot_start_x")+50,variables.get_pixel_loc("inv_slot_start_y")+70)
                utils.press_key("DropItem")
                time.sleep(0.3*settings.lag_offset)
            time.sleep(0.1*settings.lag_offset)

    player_inventory.close()
    time.sleep(0.2*settings.lag_offset)
    if temp:
        utils.turn_left(180)
    utils.turn_right(90*turn_constant)
    time.sleep(0.3*settings.lag_offset)
    inventory.open()
    if not template.template_await_true(template.check_template,2,"crop_plot",0.7):
        logs.logger.warning(f"the {direction} crop plot at {metadata.name}tp failed to open retrying now")
        utils.zero()
        utils.set_yaw(metadata.yaw)
        utils.turn_right(130*turn_constant)
        time.sleep(0.2*settings.lag_offset)
        inventory.open()
    if template.check_template("crop_plot",0.7):
        inventory.transfer_all_from()
        time.sleep(0.2*settings.lag_offset)
        player_inventory.transfer_all_inventory() #take out all input all # refreshing owl pelletes
        time.sleep(0.2*settings.lag_offset)
        inventory.close()
    time.sleep(0.2*settings.lag_offset)

    utils.turn_left(90*turn_constant)
    time.sleep(0.2*settings.lag_offset)
    inventory.open()
    if template.check_template("crop_plot",0.7):
        logs.logger.debug("failed to turn away from the crop plot retrying now")
        inventory.close()
        time.sleep(0.5*settings.lag_offset)
        utils.turn_left(90*turn_constant)
        time.sleep(0.3*settings.lag_offset)
        inventory.open()
        time.sleep(0.3*settings.lag_offset)
    if inventory.is_open():
        clean_and_feed_gacha()

    inventory.close()
    time.sleep(0.2*settings.lag_offset)
    utils.turn_left(40*turn_constant)

def collection(metadata):
    target_yaw = getattr(metadata, "target_yaw", None)
    target_pitch = getattr(metadata, "target_pitch", None)
    
    if target_yaw is not None and target_pitch is not None:
        utils.set_yaw(target_yaw)
        utils.set_pitch(target_pitch)
    else:
        # Fallback to legacy blind turning
        direction = metadata.side
        if direction == "right":
            turn_constant = 1
        else:
            turn_constant = -1
        utils.turn_right(40*turn_constant)
        
    time.sleep(0.2*settings.lag_offset)
    inventory.open()

    if inventory.is_open():
        inventory.transfer_all_from()
    inventory.close()


def drop_off_nocrop(metadata): # change reberry time or you will run out of crops
    if check_drift() == "DRIFT_DETECTED":
        return "DRIFT_DETECTED"
        
    target_yaw = getattr(metadata, "target_yaw", None)
    target_pitch = getattr(metadata, "target_pitch", None)
    
    if target_yaw is not None and target_pitch is not None:
        utils.set_yaw(target_yaw)
        utils.set_pitch(target_pitch)
    else:
        # Fallback to legacy blind turning
        direction = metadata.side
        if direction == "right":
            turn_constant = 1
        else:
            turn_constant = -1
        utils.turn_right(40*turn_constant)
        
    time.sleep(0.2*settings.lag_offset)
    inventory.open()

    if inventory.is_open():
        clean_and_feed_gacha()
    inventory.close()
    time.sleep(0.2*settings.lag_offset)


def iguanadon_gacha(metadata):
    target_yaw = getattr(metadata, "target_yaw", None)
    target_pitch = getattr(metadata, "target_pitch", None)
    
    if target_yaw is not None and target_pitch is not None:
        # Turning backwards to face the iguanadon from the gacha
        # Wait, if we use absolute aiming, does this function aim at the Gacha or the Iguanodon?
        # The original code did turn_right(180) to face the iguanadon.
        utils.set_yaw((target_yaw + 180) % 360)
        utils.set_pitch(target_pitch)
    else:
        # Fallback to legacy blind turning
        direction = metadata.side
        if direction == "right":
            turn_constant = 1
        else:
            turn_constant = -1

        utils.turn_right(180) # turning backwards to face iguaadon
        
    time.sleep(0.2*settings.lag_offset) # timer to prevent accidentle openings of the gachas 

    # put in mejos in current inventory into iguanadon should be 145 slots
    inventory.open()
    time.sleep(0.1*settings.lag_offset)
    inventory.drop_all_obj() # making sure iguanadon is empty (AT THE START ONLY - gets rid of previous seeds)
    inventory.transfer_all_from() # doing this should prevent the seed not appearing first try
    player_inventory.search_in_inventory(settings.berry_type) #iguanadon has 1450 weight for the 145 stacks of berries
    player_inventory.transfer_all_inventory()
    inventory.close()
    # exit iguanadon press e to seed
    if not template.template_await_true(template.check_template,1,"seed_inv",0.7):
        logs.logger.debug("iguanadon seeding hasnt been spotted re adding berries")
        inventory.open()
        inventory.search_in_object(settings.berry_type)
        inventory.transfer_all_from()
        player_inventory.search_in_inventory(settings.berry_type)
        player_inventory.transfer_all_inventory()
        inventory.close()
        template.template_await_true(template.check_template,1,"seed_inv",0.7)
    
    # Use Radial Wheel to Seed Berries
    logs.logger.debug("Opening radial wheel to seed berries")
    utils.key_down("Use")
    time.sleep(1.0 * settings.lag_offset) # Wait for radial wheel to open
    # Move mouse to Top Right (relative to center)
    center_x = screen.mon["width"] / 2
    center_y = screen.mon["height"] / 2
    windows.move_mouse(center_x + (300 * (screen.mon["width"] / 2560)), center_y - (300 * (screen.mon["height"] / 1440)))
    time.sleep(0.5 * settings.lag_offset)
    utils.key_up("Use")
    #seeding takes about a second till we can reaccess ∴ we either get more mejos from our shoulder mount if we need to during this time 
    # if mejoberries not in the second slot (ie we have less than 100 mejos)
        # press r to get circle menu for shoulder mount
        # press the access inv
        #ASA.dinosaurs.shoulder_mounts.access_inv
        # take out 1 stack of berry from shoulder press T once 
        # check the bottom left to see the + and - to see if the berries come out IDK Lag or smth might mess it up
        # exit out of the shoulder mount  now we have 145 slots of berrries again in theory after we take out from the iguanadon 
    # take out the seeds and add the 1 stack of mejos -> descending has mejos before the seeds of mejos ∴ are at the top of the search list 
    # we are going to be using 290 slots in the gacha - 10 extra slots allows room for pellets to be picked up by gacha
    # you have 145 seeds alr in our inv + 1 stack of berries 
    # assuming pyro is full therefore we cant use it 
    # assuming gacha is black boxed cant use that and we cant deposit all
    # turn around drop all on gacha while we have 145 seeds and depo seeds ( max drop all is about 230 slots in OUR inv)
    # we put in the seeds in our inv into the gacha 
    # turn back to iguanadon 
    # seed the iguanadon again adding the +1 berries we have and getting more from our shoulder mount if nessasary during seed animation
    # take all we have 145 seeds 145 berrys at this point
    # now turn back to the gacha we have 290 slots 
    # search for seeds
    # transfer all from char we should now just have the 144 slots of seeds from the iguanadon
    # exit gacha
    # tp away 
    #  
    #
    #


def y_trap_drop_off(metadata):
    target_yaw = getattr(metadata, "target_yaw", None)
    target_pitch = getattr(metadata, "target_pitch", None)
    
    if target_yaw is not None and target_pitch is not None:
        utils.set_yaw(target_yaw)
        utils.set_pitch(target_pitch)
    else:
        # Fallback to legacy blind turning
        direction = metadata.side
        if direction == "right":
            turn_constant = 1
        else:
            turn_constant = -1
        utils.turn_right(40*turn_constant)
        
    time.sleep(0.2*settings.lag_offset)
    inventory.open()

    if inventory.is_open():
        clean_and_feed_gacha()
        
    inventory.close()
    time.sleep(0.2*settings.lag_offset)

