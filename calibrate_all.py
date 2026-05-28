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

def main():
    print("Welcome to the Master Calibration Script!")
    print("This script will guide you through capturing perfectly accurate Yaw and Pitch")
    print("coordinates for your entire base, eliminating all blind-turning glitches!\n")

    # 1. Calibrate Gachas
    print("\n--- Calibrating Gachas ---")
    try:
        with open("json_files/gacha.json", "r") as f:
            gachas = json.load(f)
        
        for gacha in gachas:
            yaw, pitch = get_coordinates(f"Teleport to {gacha['teleporter']}."
                                         f"\nAim exactly at {gacha['name']} ({gacha['side']} side).")
            gacha["yaw"] = yaw
            gacha["pitch"] = pitch
            
        with open("json_files/gacha.json", "w") as f:
            json.dump(gachas, f, indent=4)
        print("Gachas saved!")
    except Exception as e:
        print(f"Skipping Gachas: {e}")

    # 2. Calibrate Vaults
    print("\n--- Calibrating Vaults ---")
    try:
        with open("json_files/vaults.json", "r") as f:
            vaults = json.load(f)
            
        for vault in vaults:
            yaw, pitch = get_coordinates(f"Go to your drop-off teleporter."
                                         f"\nAim exactly at the {vault['name']} ({vault['side']} side).")
            vault["yaw"] = yaw
            vault["pitch"] = pitch
            
        with open("json_files/vaults.json", "w") as f:
            json.dump(vaults, f, indent=4)
        print("Vaults saved!")
    except Exception as e:
        print(f"Skipping Vaults: {e}")

    # 3. Calibrate Dedis
    print("\n--- Calibrating Dedicated Storage ---")
    try:
        with open("json_files/dedis.json", "r") as f:
            dedis = json.load(f)
            
        for group in dedis:
            if not group.get("active", False):
                print(f"Skipping {group['dediID']} dedis (active: false)")
                continue
            print(f"Calibrating group: {group['dediID']}")
            for idx, box in enumerate(group["dediBoxes"]):
                yaw, pitch = get_coordinates(f"Go to your {group['dediID']} teleporter."
                                             f"\nAim at Dedicated Storage Box #{idx+1} ({box['resource']}).")
                box["yaw"] = yaw
                box["pitch"] = pitch
                
                ans = input("Should the bot crouch for this box? (y/n): ")
                box["crouched"] = True if ans.lower().startswith('y') else False
                
        with open("json_files/dedis.json", "w") as f:
            json.dump(dedis, f, indent=4)
        print("Dedis saved!")
    except Exception as e:
        print(f"Skipping Dedis: {e}")

    # 4. Calibrate Crop Plots
    print("\n--- Calibrating Crop Plots ---")
    try:
        with open("json_files/crop_plots.json", "r") as f:
            crops = json.load(f)
            
        print(f"Found {len(crops)} crop plots defined in JSON.")
        for idx, crop in enumerate(crops):
            yaw, pitch = get_coordinates(f"Go to your Crop Plots teleporter."
                                         f"\nAim exactly at Crop Plot #{idx+1}.")
            crop["yaw"] = yaw
            crop["pitch"] = pitch
            
            ans = input("Should the bot crouch for this crop plot? (y/n): ")
            crop["crouched"] = True if ans.lower().startswith('y') else False
            
        with open("json_files/crop_plots.json", "w") as f:
            json.dump(crops, f, indent=4)
        print("Crop Plots saved!")
    except Exception as e:
        print(f"Skipping Crop Plots: {e}")

    print("\n=======================================================")
    print("Calibration Complete! Your JSON files have been updated.")
    print("The bot will now use absolute pinpoint aiming!")

if __name__ == "__main__":
    main()
