import time
import numpy as np
import pyautogui
from mss import mss
from pynput import keyboard

#--------------------------------------------------------------------------------------------------
# ONLY CHANGE THESE SETTINGS TO AVOID BREAKING SOMETHING
TARGET_RGB = (255, 87, 34)  #put your rgb value here
TARGET_BGR = (TARGET_RGB[2], TARGET_RGB[1], TARGET_RGB[0]) #DONT change this one
TOLERANCE = 0              # set >0 to allow near-matches
SCAN_INTERVAL = 0        # seconds between scans; 0.0 = tightest loop (high CPU)
CLICK_COOLDOWN = 0.1    # tiny pause after a click to avoid infinite immediate re-clicks
CLICK_BUTTON = 'left'     # 'left' or 'right'
#------------------------------------------------------------------------------------------------

stop_flag = False

def on_press(key):
    global stop_flag
    try:
        if key.char == '`': # ( ` )stops the script
            stop_flag = True
            return False
    except AttributeError:
        pass

def start_key_listener():
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    return listener

def find_first_bgr_match(img_bgr):
    """
    img_bgr: H x W x 3 BGR numpy array (dtype=uint8)
    returns (x, y) or None
    """
    h, w, _ = img_bgr.shape
    flat = img_bgr.reshape(-1, 3)

    matches = np.all(flat == TARGET_BGR, axis=1)
    if not matches.any():
        return None
    idx = np.argmax(matches)
    y, x = divmod(idx, w)
    return int(x), int(y)

def main():
    global stop_flag

    print("Starting FAST color scanner for #bd0004 (RGB {})".format(TARGET_RGB))
    print("Press ` (backtick) to stop the script.")
    print("Ctrl+C in terminal will also stop.")
    listener = start_key_listener()

    sct = mss()
    monitor = sct.monitors[0]
    monitor_bb = {"left": monitor["left"], "top": monitor["top"],
                  "width": monitor["width"], "height": monitor["height"]}

    try:
        while not stop_flag:
            sshot = sct.grab(monitor_bb)
            img_bgr = np.asarray(sshot)[:, :, :3]
            coord = find_first_bgr_match(img_bgr)
            if coord is not None:
                x = monitor_bb["left"] + coord[0]
                y = monitor_bb["top"] + coord[1]
                pyautogui.click(x=x, y=y, button=CLICK_BUTTON)
                
                time.sleep(CLICK_COOLDOWN)
            else:
                if SCAN_INTERVAL > 0:
                    time.sleep(SCAN_INTERVAL)
                    
    except KeyboardInterrupt:
        pass
    finally:
        stop_flag = True
        try:
            listener.stop()
        except Exception:
            pass
        print("Stopped.")

if __name__ == "__main__":
    main()
