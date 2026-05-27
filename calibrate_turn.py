from source.utility import utils
from source.ASA.player import console
import time

print("Attempting to calibrate your mouse sensitivity...")
print("Please tab into Ark within 5 seconds...")
time.sleep(5)

try:
    ccc_data = console.console_ccc()
    start_yaw = float(ccc_data[3])
    print(f"Starting Yaw: {start_yaw}")

    print("Turning right exactly 90 virtual degrees...")
    utils.turn_right(90)
    time.sleep(1)

    ccc_data = console.console_ccc()
    end_yaw = float(ccc_data[3])
    print(f"Ending Yaw: {end_yaw}")

    actual_turn = end_yaw - start_yaw
    if actual_turn < 0:
        actual_turn += 360
    
    print(f"The bot tried to turn 90 degrees, but your character ACTUALLY turned {actual_turn} degrees!")
    print(f"Multiplier needed: {90 / actual_turn}")

except Exception as e:
    print(f"Error: {e}")
