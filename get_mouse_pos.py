import pyautogui
import time
import os

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

print("=== Ark Coordinate Finder ===")
print("Move your mouse over the search bar or bed slot.")
print("Press Ctrl+C to stop the script.\n")
time.sleep(2)

try:
    while True:
        x, y = pyautogui.position()
        # Print on the same line to keep the console clean
        print(f"Current Mouse Coordinates -> X: {x}, Y: {y}      ", end="\r")
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\n\nStopped.")
