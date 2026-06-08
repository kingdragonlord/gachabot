import time
import json
import settings
from source.ASA.stations import custom_stations
from source.ASA.strucutres import teleporter, inventory as struc_inventory
from source.utility import template, utils, windows, variables, screen
from source.logs import gachalogs as logs
from source.ASA import config as asa_config
from source.ASA.player import player_inventory 
def craft_gunpowder():
    # open chem bench
    struc_inventory.open()
    if not template.template_await_true(template.check_template,1,"chem_bench",0.7):
        struc_inventory.close()
        utils.zero()
        #utils.set_yaw(metadata.yaw)
    # search for gun
    if template.check_template("chem_bench",0.7):
        struc_inventory.search_in_object("gun")
        time.sleep(0.3*settings.lag_offset)
        x = struc_inventory.inv_slots["x"]
        y = struc_inventory.inv_slots["y"]
        if screen.screen_resolution == 1080:
            windows.move_mouse(x * 0.75,y * 0.75)
            windows.click(x * 0.75,y * 0.75)
        else:
            windows.move_mouse(x,y)
            windows.click(x,y)
        
        for count in range(15):
            utils.press_key("a")
    # press hover first slot
    # hold A 

    ...
def craft_sparkpowder():
    struc_inventory.open()
    if not template.template_await_true(template.check_template,1,"chem_bench",0.7):
        struc_inventory.close()
        utils.zero()
        #utils.set_yaw(metadata.yaw)
    # search for gun
    if template.check_template("chem_bench",0.7):
        struc_inventory.search_in_object("spark")
        time.sleep(0.3*settings.lag_offset)
        x = struc_inventory.inv_slots["x"]
        y = struc_inventory.inv_slots["y"]
        if screen.screen_resolution == 1080:
            windows.move_mouse(x * 0.75,y * 0.75)
            windows.click(x * 0.75,y * 0.75)
        else:
            windows.move_mouse(x,y)
            windows.click(x,y)
        
        for count in range(15):
            utils.press_key("a")
    # open chem bench
    # search for gun
    # press hover first slot
    # hold A 
    ...