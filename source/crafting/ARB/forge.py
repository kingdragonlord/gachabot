import time
import json
import settings
from source.ASA.stations import custom_stations
from source.ASA.strucutres import teleporter, inventory as struc_inventory
from source.utility import template, utils, windows, variables, screen
from source.logs import gachalogs as logs
from source.ASA import config as asa_config
from source.ASA.player import player_inventory
#import pytesseract

def indi_forge(metadata):
    struc_inventory.open()
    attempt = 0
    while not struc_inventory.is_open():
        logs.logger.debug(f"the indiforge NAME could not be accessed retrying {attempt} / {5}")
        utils.zero()
        utils.set_yaw(metadata.yaw)
        struc_inventory.open()
        if attempt >= 5:
            logs.logger.error(f"the indiforge NAME could not be accesssed after {attempt} attempts")
            break
        
    # check indi forge
    struc_inventory.transfer_all_from() # removing all cooked reasouces
    # check for 0 slots with OCR 
    # if not 0 slots exit forge depo ( will probably just be for metal but will do anyway)
    # then when slots are 0 we should transfer all again 
    player_inventory.transfer_all_inventory() 