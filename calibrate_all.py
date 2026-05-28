import json
import time
import os
import sys

# Add project root to sys.path so we can import source modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from source.ASA.player import console

def get_coordinates(prompt_text):
    print(f"\n=======================================================")
    print(f"{prompt_text}")
    print("Tab into Ark, look at the exact target, and press Enter here when ready.")
    input("Press Enter...")
    print("Waiting 3 seconds for you to tab back into Ark. DO NOT MOVE YOUR MOUSE...")
    time.sleep(3)
    try:
        ccc_data = console.console_ccc()
        yaw = float(ccc_data[3])
        pitch = float(ccc_data[4])
        print(f"Captured! Yaw: {yaw}, Pitch: {pitch}")
        return yaw, pitch
    except Exception as e:
        print(f"Error capturing coordinates: {e}")
        return 0.0, 0.0

def load_or_create(filename, default_data):
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                return json.load(f)
        except:
            pass
    return default_data

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

def normalize_yaw(yaw):
    yaw = (yaw % 360 + 360) % 360
    if yaw > 180:
        yaw -= 360
    return yaw

def main():
    print("Welcome to the GachaBot Setup & Calibration Wizard!")
    print("This script will help you configure the exact number of stations you have,")
    print("and then grab perfect pinpoint coordinates for all of them.")

    stations_file = "json_files/stations.json"
    stations = load_or_create(stations_file, [])
    
    # -----------------------------------------------------
    # GACHAS
    # -----------------------------------------------------
    try:
        num_gacha_pairs = int(input("\nHow many Gacha PAIRS do you have? (e.g. 4): ").strip() or 0)
    except:
        num_gacha_pairs = 0
        
    gachas = []
    copy_gachas = False
    gacha_offsets = {} # left/right -> (yaw_offset, pitch)
    
    if num_gacha_pairs > 1:
        ans = input("Are all your Gacha stations built IDENTICALLY? (If yes, we will only calibrate Pair 1 and copy the angles) (y/n): ").strip().lower()
        if ans.startswith('y'):
            copy_gachas = True
            
    for i in range(num_gacha_pairs):
        pair_num = i + 1
        tp_name = f"GACHAPAIR{pair_num}"
        
        # Ensure teleporter exists in stations.json
        if not any(s.get("name") == tp_name for s in stations):
            print(f"\nAdding {tp_name} to stations.json...")
            base_yaw, _ = get_coordinates(f"Teleport to {tp_name}, DO NOT MOVE YOUR CAMERA. We need the base teleporter Yaw.")
            stations.append({"name": tp_name, "xpos": 0, "ypos": 0, "zpos": 0, "yaw": base_yaw, "pitch": 0})
            save_json(stations_file, stations)
            
        base_yaw = next((s["yaw"] for s in stations if s["name"] == tp_name), 0.0)

        for side in ["left", "right"]:
            gacha_name = f"gacha{(i*2) + (1 if side=='left' else 2)}"
            
            if copy_gachas and pair_num > 1:
                print(f"Auto-calculating {gacha_name} ({side})...")
                yaw_offset, pitch = gacha_offsets[side]
                yaw = normalize_yaw(base_yaw + yaw_offset)
            else:
                yaw, pitch = get_coordinates(f"Teleport to {tp_name}. Aim exactly at {gacha_name} ({side} side).")
                if copy_gachas and pair_num == 1:
                    yaw_offset = normalize_yaw(yaw - base_yaw)
                    gacha_offsets[side] = (yaw_offset, pitch)

            gachas.append({
                "name": gacha_name,
                "teleporter": tp_name,
                "resource_type": "element",
                "side": side,
                "yaw": yaw,
                "pitch": pitch
            })
            
    save_json("json_files/gacha.json", gachas)

    # -----------------------------------------------------
    # VAULTS
    # -----------------------------------------------------
    try:
        num_vaults = int(input("\nHow many Vaults do you have? (e.g. 2): ").strip() or 0)
    except:
        num_vaults = 0
        
    vaults = []
    for i in range(num_vaults):
        side = "left" if i % 2 == 0 else "right"
        items = input(f"What items go in Vault #{i+1} ({side} side)? (comma separated, e.g. metal,stone): ").strip().split(',')
        yaw, pitch = get_coordinates(f"Go to your drop-off teleporter. Aim exactly at Vault #{i+1} ({side} side).")
        vaults.append({
            "name": f"vault{i+1}",
            "side": side,
            "items": [item.strip() for item in items if item.strip()],
            "yaw": yaw,
            "pitch": pitch
        })
    save_json("json_files/vaults.json", vaults)

    # -----------------------------------------------------
    # DEDIS
    # -----------------------------------------------------
    try:
        num_dedi_groups = int(input("\nHow many Dedicated Storage GROUPS do you have? (e.g. 1): ").strip() or 0)
    except:
        num_dedi_groups = 0
        
    dedis = []
    for i in range(num_dedi_groups):
        group_id = input(f"What is the ID for Dedi Group #{i+1}? (e.g. deposit or grindables): ").strip()
        try:
            num_boxes = int(input(f"How many boxes in group '{group_id}'? ").strip() or 0)
        except:
            num_boxes = 0
            
        boxes = []
        for j in range(num_boxes):
            resource = input(f"What resource goes in Box #{j+1}? (e.g. element, metal): ").strip()
            yaw, pitch = get_coordinates(f"Go to your {group_id} teleporter. Aim exactly at {resource} Box #{j+1}.")
            crouch = input("Should the bot crouch for this box? (y/n): ").strip().lower().startswith('y')
            boxes.append({
                "resource": resource,
                "crouched": crouch,
                "yaw": yaw,
                "pitch": pitch
            })
            
        dedis.append({
            "dediID": group_id,
            "active": True,
            "dediBoxes": boxes
        })
    save_json("json_files/dedis.json", dedis)

    # -----------------------------------------------------
    # PEGO STATIONS
    # -----------------------------------------------------
    try:
        num_pegos = int(input("\nHow many Pego stations do you have? (e.g. 1): ").strip() or 0)
    except:
        num_pegos = 0
        
    pegos = []
    for i in range(num_pegos):
        tp_name = f"pego{i+1}"
        delay = 3300 # default delay
        
        # Ensure teleporter exists in stations.json
        if not any(s.get("name") == tp_name for s in stations):
            print(f"\nAdding {tp_name} to stations.json...")
            base_yaw, _ = get_coordinates(f"Teleport to {tp_name}, DO NOT MOVE YOUR CAMERA. We need the base teleporter Yaw.")
            stations.append({"name": tp_name, "xpos": 0, "ypos": 0, "zpos": 0, "yaw": base_yaw, "pitch": 0})
            save_json(stations_file, stations)
            
        pegos.append({
            "name": tp_name,
            "teleporter": tp_name,
            "delay": delay
        })
    save_json("json_files/pego.json", pegos)

    # -----------------------------------------------------
    # CROP PLOTS
    # -----------------------------------------------------
    try:
        num_crops = int(input("\nHow many Crop Plots do you have? (e.g. 8): ").strip() or 0)
    except:
        num_crops = 0
        
    crops = []
    for i in range(num_crops):
        yaw, pitch = get_coordinates(f"Go to your Crop Plots teleporter. Aim exactly at Crop Plot #{i+1}.")
        crouch = input("Should the bot crouch for this crop plot? (y/n): ").strip().lower().startswith('y')
        crops.append({
            "yaw": yaw,
            "pitch": pitch,
            "crouched": crouch
        })
    save_json("json_files/crop_plots.json", crops)

    print("\n=======================================================")
    print("Setup and Calibration Complete! Your JSON files have been fully generated.")
    print("The bot will now use absolute pinpoint aiming!")

if __name__ == "__main__":
    main()
