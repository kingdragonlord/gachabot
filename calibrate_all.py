import os
import time
import json
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
    print("This script will help you configure your massive factory dynamically!")

    stations_file = "json_files/stations.json"
    stations = load_or_create(stations_file, [])
    
    # --- PREFIXES ---
    print("\n--- Teleporter Base Names & Prefixes ---")
    gacha_prefix = input("Base name for Gacha Pairs (e.g., GachaBot_gachapair): ").strip() or "GachaBot_gachapair"
    pego_prefix = input("Base name for Pego Stations (e.g., GachaBot_Pego): ").strip() or "GachaBot_Pego"
    ytrap_prefix = input("Base name for Y-Trap Stations (e.g., GachaBot_ytrap): ").strip() or "GachaBot_ytrap"
    
    render_tp = input("Name of your Render/Bed Spawn Teleporter (e.g., GachaBot_Render): ").strip() or "GachaBot_Render"
    vault_tp = input("Name of your Vault/Dropoff Teleporter (e.g., GachaBot_vault01): ").strip() or "GachaBot_vault01"
    dedi_tp = input("Name of your Dedi Teleporter (e.g., GachaBot_Dedi01): ").strip() or "GachaBot_Dedi01"
    grindables_tp = input("Name of your Grindables Teleporter (e.g., GachaBot_Grindables01): ").strip() or "GachaBot_Grindables01"

    for single_tp in [render_tp, vault_tp, dedi_tp, grindables_tp]:
        if not any(s.get("name") == single_tp for s in stations):
            print(f"Adding {single_tp} to stations.json... (Defaulting to Search Bar -1)")
            stations.append({"name": single_tp, "xpos": -1, "ypos": -1, "zpos": -1, "yaw": 0.0, "pitch": 0.0})
    save_json(stations_file, stations)

    # -----------------------------------------------------
    # TEK BED (RENDER STATION)
    # -----------------------------------------------------
    ans = input(f"\nDo you want to calibrate the Tek Bed location for {render_tp}? (y/n): ").strip().lower()
    if ans.startswith('y'):
        base_yaw, _ = get_coordinates(f"Teleport to {render_tp}, DO NOT MOVE YOUR CAMERA. We need the base teleporter Yaw.")
        yaw, pitch = get_coordinates(f"Aim exactly at the Tek Bed.")
        
        # Calculate the relative turn offset needed from the spawn point
        target_yaw = normalize_yaw(yaw - base_yaw)
        
        for s in stations:
            if s["name"] == render_tp:
                s["yaw"] = 0.0 # Force base yaw to 0 so the relative turn works perfectly
                s["target_yaw"] = target_yaw
                s["target_pitch"] = pitch
                break
        save_json(stations_file, stations)

    # -----------------------------------------------------
    # VAULTS
    # -----------------------------------------------------
    try:
        num_vaults = int(input("\nHow many Vaults do you have? (e.g. 3): ").strip() or 0)
    except:
        num_vaults = 0
        
    if num_vaults > 0:
        vaults = []
        for i in range(num_vaults):
            side = "left" if i % 2 == 0 else "right"
            items = input(f"What items go in Vault #{i+1} ({side} side)? (comma separated, e.g. mastercraft,journeyman,metal): ").strip().split(',')
            yaw, pitch = get_coordinates(f"Teleport to {vault_tp}. Aim exactly at Vault #{i+1} ({side} side).")
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
        
    if num_dedi_groups > 0:
        dedis = []
        for i in range(num_dedi_groups):
            group_id = input(f"What is the ID for Dedi Group #{i+1}? (e.g. deposit or grindables): ").strip()
            current_tp = input(f"What teleporter is Dedi Group '{group_id}' located at? (e.g. {dedi_tp} or {grindables_tp}): ").strip() or dedi_tp
            try:
                num_boxes = int(input(f"How many boxes in group '{group_id}'? ").strip() or 0)
            except:
                num_boxes = 0
                
            boxes = []
            for j in range(num_boxes):
                resource = input(f"What resource goes in Box #{j+1}? (e.g. element, metal): ").strip()
                yaw, pitch = get_coordinates(f"Teleport to {current_tp}. Aim exactly at {resource} Box #{j+1}.")
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
    # GRINDERS
    # -----------------------------------------------------
    grinder_data = {}
    
    # Vault Grinder (Deposit)
    ans1 = input("\nDo you want to calibrate the Grinder location at your VAULT teleporter? (y/n): ").strip().lower()
    if ans1.startswith('y'):
        yaw, pitch = get_coordinates(f"Teleport to {vault_tp}. Aim exactly at the Grinder.")
        grinder_data["deposit_yaw"] = yaw
        grinder_data["deposit_pitch"] = pitch

    # Grindables Grinder (Collect)
    ans2 = input("\nDo you want to calibrate the Grinder location at your GRINDABLES teleporter? (y/n): ").strip().lower()
    if ans2.startswith('y'):
        yaw, pitch = get_coordinates(f"Teleport to {grindables_tp}. Aim exactly at the Grinder.")
        grinder_data["collect_yaw"] = yaw
        grinder_data["collect_pitch"] = pitch

    if grinder_data:
        save_json("json_files/grinder.json", grinder_data)

    # -----------------------------------------------------
    # PEGO STATIONS
    # -----------------------------------------------------
    try:
        num_pegos = int(input("\nHow many Pego stations do you have? (e.g. 4): ").strip() or 0)
    except:
        num_pegos = 0
        
    if num_pegos > 0:
        pegos = []
        for i in range(num_pegos):
            tp_name = f"{pego_prefix}{i+1:02d}"
            delay = 3300 # default delay
            
            if not any(s.get("name") == tp_name for s in stations):
                print(f"Adding {tp_name} to stations.json... (Defaulting to Search Bar -1)")
                stations.append({"name": tp_name, "xpos": -1, "ypos": -1, "zpos": -1, "yaw": 0, "pitch": 0})
                save_json(stations_file, stations)
                
            yaw, pitch = get_coordinates(f"Teleport to {tp_name}. Aim exactly at Pego #{i+1}.")
            
            pegos.append({
                "name": tp_name,
                "teleporter": tp_name,
                "delay": delay,
                "yaw": yaw,
                "pitch": pitch
            })
        save_json("json_files/pego.json", pegos)

    # -----------------------------------------------------
    # GACHAS
    # -----------------------------------------------------
    try:
        num_gacha_pairs = int(input("\nHow many Gacha PAIRS do you have? (e.g. 18): ").strip() or 0)
    except:
        num_gacha_pairs = 0
        
    if num_gacha_pairs > 0:
        gachas = []
        copy_gachas = False
        gacha_offsets = {} 
        
        if num_gacha_pairs > 1:
            ans = input("Are all your Gacha stations built IDENTICALLY? (If yes, we will only calibrate Pair 1 and copy the angles) (y/n): ").strip().lower()
            if ans.startswith('y'):
                copy_gachas = True
                
        for i in range(num_gacha_pairs):
            pair_num_str = f"{i+1:02d}"
            tp_name = f"{gacha_prefix}{pair_num_str}"
            
            if not any(s.get("name") == tp_name for s in stations):
                print(f"\nAdding {tp_name} to stations.json... (Defaulting X, Y, Z to -1)")
                if copy_gachas and i > 0:
                     base_yaw = 0.0
                else:
                     base_yaw, _ = get_coordinates(f"Teleport to {tp_name}, DO NOT MOVE YOUR CAMERA. We need the base teleporter Yaw.")
                stations.append({"name": tp_name, "xpos": -1, "ypos": -1, "zpos": -1, "yaw": base_yaw, "pitch": 0})
                save_json(stations_file, stations)
                
            base_yaw = next((s["yaw"] for s in stations if s["name"] == tp_name), 0.0)

            for side in ["left", "right"]:
                gacha_name = f"gacha{(i*2) + (1 if side=='left' else 2)}"
                
                if copy_gachas and i > 0:
                    print(f"Auto-calculating {gacha_name} ({side})...")
                    yaw_offset, pitch = gacha_offsets[side]
                    yaw = normalize_yaw(base_yaw + yaw_offset)
                else:
                    yaw, pitch = get_coordinates(f"Teleport to {tp_name}. Aim exactly at {gacha_name} ({side} side).")
                    if copy_gachas and i == 0:
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
    # Y-TRAP STATIONS
    # -----------------------------------------------------
    try:
        num_ytraps = int(input("\nHow many Y-Trap STATIONS do you have? (e.g. 18): ").strip() or 0)
    except:
        num_ytraps = 0

    if num_ytraps > 0:
        for i in range(num_ytraps):
            tp_name = f"{ytrap_prefix}{i+1:02d}"
            if not any(s.get("name") == tp_name for s in stations):
                stations.append({"name": tp_name, "xpos": -1, "ypos": -1, "zpos": -1, "yaw": 0, "pitch": 0})
        save_json(stations_file, stations)
        
        try:
            num_plots = int(input("\nHow many Crop Plots per stack? (e.g. 8): ").strip() or 0)
        except:
            num_plots = 0
            
        if num_plots > 0:
            print("\nWe will calibrate the crop plots for the FIRST Y-Trap station only. The bot assumes the rest are built identically!")
            left_plots = []
            right_plots = []
            
            base_yaw, _ = get_coordinates(f"Teleport to {ytrap_prefix}01, DO NOT MOVE YOUR CAMERA. We need the base teleporter Yaw.")
            
            # Left Stack
            print(f"\n--- Calibrating {num_plots} LEFT Stack Crop Plots ---")
            for j in range(num_plots):
                yaw, pitch = get_coordinates(f"Aim exactly at LEFT Stack Crop Plot #{j+1}.")
                crouch = input("Should the bot crouch for this crop plot? (y/n): ").strip().lower().startswith('y')
                left_plots.append({"yaw": normalize_yaw(yaw - base_yaw), "pitch": pitch, "crouched": crouch})
            save_json("json_files/ytrap_left_plots.json", left_plots)
            
            # Right Stack
            print(f"\n--- Calibrating {num_plots} RIGHT Stack Crop Plots ---")
            for j in range(num_plots):
                yaw, pitch = get_coordinates(f"Aim exactly at RIGHT Stack Crop Plot #{j+1}.")
                crouch = input("Should the bot crouch for this crop plot? (y/n): ").strip().lower().startswith('y')
                right_plots.append({"yaw": normalize_yaw(yaw - base_yaw), "pitch": pitch, "crouched": crouch})
            save_json("json_files/ytrap_right_plots.json", right_plots)

    print("\n=======================================================")
    print("Setup and Calibration Complete! Your JSON files have been fully generated.")

if __name__ == "__main__":
    main()
