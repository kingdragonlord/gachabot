from source.ASA.player import player_inventory , player_state
from source.logs import gachalogs as logs
from source.utility import utils ,template , windows ,variables ,screen ,local_player
import time 
import settings
import source.ASA.config
import pyautogui
import win32clipboard

last_command = ""

def is_open():
    return template.console_strip_check(template.console_strip_bottom(), is_bottom=True) or template.console_strip_check(template.console_strip_middle(), is_bottom=False)

def enter_data(data:str):
    global last_command
    if source.ASA.config.up_arrow and data == last_command:
        logs.logger.debug(f"using uparrow to put {data} into the console")
        pyautogui.press("up")
    else:
        logs.logger.debug(f"using clipboard to put {data} into the console")
        clipboard_opened = False
        try: # my pc had issues where it would run threw this and not open clipoard then crash trying to close it
            win32clipboard.OpenClipboard()
            clipboard_opened = True
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(data, win32clipboard.CF_TEXT)
        except Exception as e:
            print(f"Clipboard error: {e}")
        finally:
            if clipboard_opened:
                win32clipboard.CloseClipboard()
        pyautogui.hotkey("ctrl","v")
    last_command = data
    
def console_ccc():
    data = None
    attempts = 0
    while data == None:
        attempts += 1
        logs.logger.debug(f"trying to get ccc data {attempts} / {source.ASA.config.console_ccc_attempts}")
        player_state.reset_state() #reset state at the start to make sure we can open up the console window
        time.sleep(0.5 * settings.lag_offset) # wait for any UI closing animations to finish before pressing console key
        # Blindly press ConsoleKeys to open console
        utils.press_key("ConsoleKeys")
        time.sleep(0.3 * settings.lag_offset) # wait for console to open visually
        
        # CLEAR THE CLIPBOARD BEFORE DOING ANYTHING to prevent reading old data on failure
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.CloseClipboard()
        except Exception:
            pass

        if attempts >= source.ASA.config.console_ccc_attempts:
            # Type manually
            last_command = "ccc"
            enter_data("ccc")
            time.sleep(0.1*settings.lag_offset)
            utils.press_key("Enter")
        else: 
            enter_data("ccc")
            time.sleep(0.1*settings.lag_offset)
            utils.press_key("Enter")
            
        time.sleep(0.1*settings.lag_offset) # slow to try and prevent opening clipboard to empty data
        try:
            win32clipboard.OpenClipboard()
            data = win32clipboard.GetClipboardData()
            win32clipboard.EmptyClipboard()
        except Exception:
            pass
        finally:
            try:
                win32clipboard.CloseClipboard()
            except:
                pass
        
        if data is None:
            # If data is None, we failed to get CCC coordinates. 
            # This almost always means the console wasn't open and we accidentally opened the chat instead.
            # Press Escape to close the chat so we don't get stuck typing commands into it.
            logs.logger.warning("Failed to get CCC data! Pressing Escape to clear chat box.")
            utils.press_key("Escape")
            time.sleep(0.5 * settings.lag_offset)

        if attempts >= source.ASA.config.console_ccc_attempts:
            logs.logger.error(f"CCC is still returning NONE after {attempts} attempts")
            break        
    if data != None:    
        ccc_data = data.split()
        return ccc_data
    return data

def console_write(text:str):
    global last_command
    # Blindly press ConsoleKeys to open console
    utils.press_key("ConsoleKeys")
    time.sleep(0.3 * settings.lag_offset)

    enter_data(text)
    time.sleep(0.1*settings.lag_offset)
    utils.press_key("Enter")
    
    last_command = text
    time.sleep(0.1*settings.lag_offset)

def close_console(middle):
    '''
    We no longer use this as we do blind execution
    '''
    pass