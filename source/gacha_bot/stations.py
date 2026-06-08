import time
import json
import settings
from source.utility import utils ,template , windows ,variables ,screen ,local_player
from source.logs import gachalogs as logs
from source.ASA.strucutres import teleporter , inventory ,bed
from source.ASA.stations import custom_stations
from source.ASA.player import player_inventory , player_state ,console , tribelog
import source.gacha_bot.config 
import source.gacha_bot.render
from source.gacha_bot import config , deposit , gacha , iguanadon , pego , render
from abc import ABC ,abstractmethod

class StationState:
    berry_station = True
    last_berry = 0

state = StationState()

class base_task(ABC):
    def __init__(self):
        self.has_run_before = False
        
    @abstractmethod
    def execute(self):
        pass
    @abstractmethod
    def get_priority_level(self):
        pass
    @abstractmethod
    def get_requeue_delay(self):
        pass
    
    def mark_as_run(self):
        self.has_run_before = True

class gacha_station(base_task):
    def __init__(self,name,teleporter_name,direction):
        super().__init__()
        self.name = name
        self.teleporter_name = teleporter_name # also the same as bed name for y
        self.direction = direction


    def execute(self):
        player_state.check_state(False)
        
        temp = False
        time_between = time.time() - state.last_berry

        gacha_metadata = custom_stations.get_station_metadata(self.teleporter_name)
        gacha_metadata.side = self.direction
        
        # Load absolute yaw and pitch from gacha.json
        try:
            with open("json_files/gacha.json", "r") as f:
                gachas = json.load(f)
            for g in gachas:
                if g["name"] == self.name:
                    gacha_metadata.target_yaw = g.get("yaw", None)
                    gacha_metadata.target_pitch = g.get("pitch", None)
                    break
        except Exception as e:
            logs.logger.debug(f"Failed to load gacha.json absolute coordinates: {e}")

        berry_metadata = custom_stations.get_station_metadata(settings.berry_station)
        iguanadon_metadata = custom_stations.get_station_metadata(settings.iguanadon)
        if settings.y_trap_bot:
            time.sleep(0.2)
            # Extract number from teleporter name to map to the correct ytrap station
            import re
            match = re.search(r'\d+', self.teleporter_name)
            if match:
                ytrap_num = match.group()
                # Use standard prefix mapping, defaulting back if the user somehow uses old names
                ytrap_name = f"GachaBot_ytrap{ytrap_num}"
            else:
                ytrap_name = "ytrap1"

            # Teleport to the y-trap teleporter
            ytrap_metadata = custom_stations.get_station_metadata(ytrap_name)
            teleporter.teleport_not_default(ytrap_metadata)
            
            # Harvest the respective stack (left or right)
            import source.gacha_bot.structures.crop_plots as crop_plots
            crop_plots.harvest_stack(self.direction)
            
            # Teleport back to the gacha
            teleporter.teleport_not_default(gacha_metadata)
            
            # Drop off the y-traps
            gacha.y_trap_drop_off(gacha_metadata)

        else:
            if (state.berry_station or time_between > source.gacha_bot.config.time_to_reberry*60*60): # if time is greater than 4 hours since the last time you went to berry station 
                teleporter.teleport_not_default(berry_metadata)                    # or if berry station is true( when you go to tekpod and drop all ) and the time between has been longer than 30 mins since youve last been 
                if settings.external_berry: 
                    logs.logger.debug("sleeping for 20 seconds as external")
                    time.sleep(20)#letting station spawn in if you have to tp away
                iguanadon.berry_station()
                state.last_berry = time.time()
                state.berry_station = False
                temp = True
            
            teleporter.teleport_not_default(iguanadon_metadata) # iguanadon is a centeral tp
            
            if settings.external_berry and temp: # quick fix for level 1 bug
                logs.logger.debug("reconnecting because of level 1 bug - you chose external berry will sleep for 60 seconds as a way to ensure that we are fully loaded in")
                console.console_write("reconnect")
                time.sleep(60) # takes a while for the reonnect to actually go into action

            iguanadon.iguanadon(iguanadon_metadata)
            teleporter.teleport_not_default(gacha_metadata)
            if settings.side_crop_plot:
                status = gacha.drop_off(gacha_metadata)
            else:
                status = gacha.drop_off_nocrop(gacha_metadata)
                
            if status == "DRIFT_DETECTED":
                logs.logger.warning(f"Aborting {self.name} due to drift. Triggering bed realignment.")
                from task_manager import task_scheduler
                scheduler = task_scheduler()
                # Queue a realign task at priority 1 (highest) so it runs immediately
                realign_task = realign_station("drift_realign")
                scheduler.add_task(realign_task, priority_flag=True)
                # Mark self as NOT run so it gets requeued to try again after realign
                self.has_run_before = False
                return

    def get_priority_level(self):
        return 3
    
    def get_requeue_delay(self):
        return 0 

class pego_station(base_task):
    def __init__(self,name,teleporter_name,delay):
        super().__init__()
        self.name = name
        self.teleporter_name = teleporter_name
        self.delay = delay

    def execute(self):
        player_state.check_state(False)
        
        pego_metadata = custom_stations.get_station_metadata(self.teleporter_name)
        dropoff_metadata = custom_stations.get_station_metadata(settings.drop_off)

        teleporter.teleport_not_default(pego_metadata)
        pego.pego_pickup(pego_metadata)
        if template.check_template("crystal_in_hotbar",0.7):
            teleporter.teleport_not_default(dropoff_metadata) # everytime you collect you have to drop off makes sense to include it into here 
            deposit.deposit_all(dropoff_metadata)
        else:
            logs.logger.info(f"bot has no crystals in hotbar we are skipping the deposit step")

    def get_priority_level(self):
        return 2 # Match gacha_station priority to enable perfect round-robin looping

    def get_requeue_delay(self):
        return self.delay
    
    
class render_station(base_task):
    def __init__(self):
        super().__init__()
        self.name = settings.bed_spawn
        
    def execute(self):
        state.berry_station = True # setting to true as we will be away for mostlikly for a few hours
        if source.gacha_bot.render.render_flag == False:
            logs.logger.debug(f"render flag{render.render_flag} we are trying to get into the pod now")
            player_state.reset_state()
            teleporter.teleport_not_default(settings.bed_spawn)
            render_metadata = custom_stations.get_station_metadata(settings.bed_spawn)
            render.enter_tekpod(render_metadata)
            player_inventory.open()
            player_inventory.drop_all_inv()
            player_inventory.close()
            tribelog.open()
    def get_priority_level(self):
        return 3 # Match gacha_station priority to enable perfect round-robin looping

    def get_requeue_delay(self):
        return 0

class realign_station(base_task):
    def __init__(self, name="realign"):
        super().__init__()
        self.name = name
        
    def execute(self):
        player_state.check_state(False)
        logs.logger.info(f"Realigning character at {settings.bed_spawn}")
        teleporter.teleport_not_default(settings.bed_spawn)
        render_metadata = custom_stations.get_station_metadata(settings.bed_spawn)
        render.enter_tekpod(render_metadata)
        
        from source.ASA.player import tribelog
        tribelog.open()
        time.sleep(2)
        
    def get_priority_level(self):
        return 3

    def get_requeue_delay(self):
        return 6600

    
class snail_pheonix(base_task):
    def __init__(self,name,teleporter_name,direction,depo):
        super().__init__()
        self.name = name
        self.teleporter_name = teleporter_name
        self.direction = direction
        self.depo_tp = depo

    def execute(self):
        gacha_metadata = custom_stations.get_station_metadata(self.teleporter_name)
        gacha_metadata.side = self.direction

        # Load absolute yaw and pitch from gacha.json
        try:
            with open("json_files/gacha.json", "r") as f:
                gachas = json.load(f)
            for g in gachas:
                if g["name"] == self.name:
                    gacha_metadata.target_yaw = g.get("yaw", None)
                    gacha_metadata.target_pitch = g.get("pitch", None)
                    break
        except Exception as e:
            logs.logger.debug(f"Failed to load gacha.json absolute coordinates: {e}")

        player_state.check_state()
        teleporter.teleport_not_default(gacha_metadata)
        gacha.collection(gacha_metadata)
        teleporter.teleport_not_default(self.depo_tp)
        deposit.dedi_deposit("element", settings.height_ele, gacha_metadata.yaw)
        
    def get_priority_level(self):
        return 4
    def get_requeue_delay(self):
        return 13200

class pause(base_task):
    def __init__(self,time):
        super().__init__()
        self.name = "pause"
        self.time = time
    def execute(self):
        player_state.check_state()
        teleporter.teleport_not_default(settings.bed_spawn)
        render_metadata = custom_stations.get_station_metadata(settings.bed_spawn)
        render.enter_tekpod(render_metadata)
        time.sleep(self.time)
        render.leave_tekpod()
        
    def get_priority_level(self):
        return 1

    def get_requeue_delay(self):
        return 0  

class crafting(base_task):
    def __init__(self):
        ...
    def execute(self):
        ...
    def get_priority_level(self):
        return 7
    
    def get_requeue_delay(self):
        return 90
    
class transfer(base_task):

    def __init__(self):
        ...
    def execute(self):
        ...
    def get_priority_level(self):
        return 
    
    def get_requeue_delay(self):
        return 0