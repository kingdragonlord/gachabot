import cv2
import numpy as np

img = cv2.imread('ark_inv_screen.png')
tpl = cv2.imread('assets/icons1080/inventory.png')

best_val = 0
best_scale = 1.0
best_loc = (0,0)

tpl_hsv = cv2.cvtColor(tpl, cv2.COLOR_BGR2HSV)
tpl_mask = cv2.inRange(tpl_hsv, np.array([0,30,200]), np.array([255,255,255]))
tpl_masked = cv2.bitwise_and(tpl, tpl, mask=tpl_mask)
tpl_gray = cv2.cvtColor(tpl_masked, cv2.COLOR_BGR2GRAY)

img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(img_hsv, np.array([0,30,200]), np.array([255,255,255]))
masked = cv2.bitwise_and(img, img, mask=mask)
gray = cv2.cvtColor(masked, cv2.COLOR_BGR2GRAY)

for scale in np.linspace(0.8, 1.2, 41):
    scaled_tpl = cv2.resize(tpl_gray, (0,0), fx=scale, fy=scale)
    res = cv2.matchTemplate(gray, scaled_tpl, cv2.TM_CCOEFF_NORMED)
    _, max_v, _, max_l = cv2.minMaxLoc(res)
    if max_v > best_val:
        best_val = max_v
        best_scale = scale
        best_loc = max_l

print('Best match:', best_val, 'at scale', best_scale, 'loc', best_loc)
