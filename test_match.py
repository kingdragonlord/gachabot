from source.utility import template, screen
import cv2
import numpy as np

def test_tpl(item, no_bounds=False):
    region = template.roi_regions[item]
    roi = screen.get_screen_roi(int(region['start_x']*0.75), int(region['start_y']*0.75), int(region['width']*0.75), int(region['height']*0.75))
    lower = np.array([0,0,0]) if no_bounds else np.array([0,30,200])
    hsv = cv2.cvtColor(roi,cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv,lower,np.array([255,255,255]))
    masked = cv2.bitwise_and(roi, roi, mask=mask)
    gray = cv2.cvtColor(masked, cv2.COLOR_BGR2GRAY)
    
    img = cv2.imread(f'assets/icons1080/{item}.png')
    img_hsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    img_mask = cv2.inRange(img_hsv,lower,np.array([255,255,255]))
    img_masked = cv2.bitwise_and(img, img, mask=img_mask)
    img_gray = cv2.cvtColor(img_masked,cv2.COLOR_BGR2GRAY)
    
    res = cv2.matchTemplate(gray, img_gray, cv2.TM_CCOEFF_NORMED)
    min_v, max_v, min_l, max_l = cv2.minMaxLoc(res)
    print(f'{item} max_val:', max_v)

test_tpl('inventory', False)
test_tpl('tribelog_check', True)
