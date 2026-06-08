import os

replacements = {
    "import ASA.stations\nimport ASA.stations.custom_stations\nimport ASA.strucutres\nimport ASA.strucutres.teleporter\nimport template\nimport logs.gachalogs as logs\nimport utils\nimport windows\nimport variables\nimport time \nimport settings\nimport ASA.config \nimport ASA.strucutres.inventory\nimport ASA.player.player_inventory\nimport bot.config\nimport json\nimport screen": 
"""import time
import json
import settings
from source.ASA.stations import custom_stations
from source.ASA.strucutres import teleporter, inventory as struc_inventory
from source.utility import template, utils, windows, variables, screen
from source.logs import gachalogs as logs
from source.ASA import config as asa_config
from source.ASA.player import player_inventory""",
    
    "ASA.strucutres.inventory": "struc_inventory",
    "ASA.player.player_inventory": "player_inventory",
    "bot.config.gacha_attempts": "5",
    "import template": "from source.utility import template"
}

files_to_fix = [
    r"C:\bot\2601\gachabot\source\crafting\replicatior.py",
    r"C:\bot\2601\gachabot\source\crafting\ARB\chembench.py",
    r"C:\bot\2601\gachabot\source\crafting\ARB\forge.py",
    r"C:\bot\2601\gachabot\source\crafting\ARB\resource_checks.py"
]

for fpath in files_to_fix:
    with open(fpath, "r") as f:
        content = f.read()
    
    for old, new in replacements.items():
        content = content.replace(old, new)
        
    with open(fpath, "w") as f:
        f.write(content)
