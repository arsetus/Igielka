import win32con
import win32gui
import win32ui
import win32api
import math
from PIL import Image, ImageSequence, ImageFile
import numpy as np
import cv2
import os
import json

def get_window_size(hwnd):
    if hwnd:
        rect = win32gui.GetWindowRect(hwnd)
        #title_bar_height = win32api.GetSystemMetrics(win32con.SM_CYCAPTION)
        x = rect[0]
        y = rect[1]
        width = rect[2] - rect[0]
        height = rect[3] - rect[1]
        return (x, y, width - 2 * win32api.GetSystemMetrics(win32con.SM_CXFRAME), height - win32api.GetSystemMetrics(win32con.SM_CYCAPTION) - 2 * win32api.GetSystemMetrics(win32con.SM_CYFRAME))
    return None

def delete_item(list_widget, item) -> None:
    index = list_widget.row(item)
    list_widget.takeItem(index)


def manage_profile(action: str, directory: str, profile_name: str, data: dict = None):
    file_path = os.path.join(directory, f"{profile_name}.json")
    if action.lower() == "save":
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)
        return True
    elif action.lower() == "load":
        if not os.path.exists(file_path):
            return {}
        with open(file_path, "r") as f:
            return json.load(f)

def calculate_direction(player_x, player_y, target_x, target_y):
    dx = target_x - player_x
    dy = target_y - player_y
    if dy == -1:
        if dx == -1: return 7
        if dx == 0: return 8
        if dx == 1: return 9
    elif dy == 0:
        if dx == -1: return 4
        if dx == 0: return 5
        if dx == 1: return 6
    elif dy == 1:
        if dx == -1: return 1
        if dx == 0: return 2
        if dx == 1: return 3 
    return 5
def getDirToPos(x,y, tX,tY, diagonal):
    dx = x - tX
    dy = y - tY

    if diagonal and abs(dy) == abs(dx):
        if dy < 0:
            if dx < 0:
                return 3
            else:
                return 1
        else:
            if dx < 0:
                return 9
            else:
                return 7
    elif abs(dy) > abs(dx):
        if dy < 0:
            return 2
        else:
            return 8
    else:
        if dx < 0:
            return 6
        else:
            return 4
#-------------------------------------------------------------------------------------------------------------------

def capture_window_by_identifier(hwnd):
    try:
        # Get the window size and position
        left, top, right, bot = win32gui.GetWindowRect(hwnd)
        width = right - left
        height = bot - top

        # Set up device context (DC) for screen and window
        hwndDC = win32gui.GetWindowDC(hwnd)
        mfcDC = win32ui.CreateDCFromHandle(hwndDC)
        saveDC = mfcDC.CreateCompatibleDC()

        # Create a compatible bitmap and select it into the DC
        saveBitMap = win32ui.CreateBitmap()
        saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
        saveDC.SelectObject(saveBitMap)

        # Copy the window content to the bitmap
        saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)

        # Get the bitmap data and convert to PIL Image
        bmpinfo = saveBitMap.GetInfo()
        bmpstr = saveBitMap.GetBitmapBits(True)
        
        img_pil = Image.frombuffer(
            'RGB',
            (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
            bmpstr, 'raw', 'BGRX', 0, 1
        )

        # Cleanup
        win32gui.DeleteObject(saveBitMap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwndDC)

        # Convert PIL Image to OpenCV NumPy array (BGR format)
        img_np = np.array(img_pil)
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

        return img_bgr

    except Exception as e:
        print(f"An error occurred during window capture: {e}")
        return None

import cv2
import numpy as np

# Assuming capture_window_by_identifier, cv2.groupRectangles, etc., are available.

def match_template_multiscale(hwnd, template_path, threshold):
    template_bgr = cv2.imread(template_path)
    img_bgr = capture_window_by_identifier(hwnd) # Assuming this returns the screen image
    
    if template_bgr is None:
        raise FileNotFoundError(f"Template file not found at: {template_path}")

    # The image captured from the screen (img_bgr) is the search area
    img_gray = img_bgr 
    tH, tW = template_bgr.shape[:2] # Original template dimensions

    all_matches = [] 

    scales = np.linspace(1.0, 3.0, 6) # e.g., [1.0, 1.4, 1.8, 2.2, 2.6, 3.0]
    
    for scale in scales:
        # Resize the template
        resized_template = cv2.resize(template_bgr, (int(tW * scale), int(tH * scale)))
        rW, rH = resized_template.shape[:2] # Scaled template dimensions
        
        # Check if the template fits on the screen
        if rW > img_gray.shape[1] or rH > img_gray.shape[0]:
            continue

        resized_template_gray = resized_template
        
        # Perform the template matching
        result_map = cv2.matchTemplate(img_gray, resized_template_gray, cv2.TM_CCOEFF_NORMED)
        loc = np.where(result_map >= threshold)

        for pt in zip(*loc[::-1]):
            x, y = pt # Top-left corner of the match
            center_x = x + (rW // 2) 
            center_y = y + (rH // 2)
            all_matches.append([center_x, center_y, rW, rH, scale])
    temp_rectangles = []
    for match in all_matches:
        # To simplify, we re-create the top-left corner box based on the center
        center_x, center_y, rW, rH, scale = match
        temp_rectangles.append([center_x - rW//2, center_y - rH//2, rW, rH])

    rectangles, weights = cv2.groupRectangles(temp_rectangles, 1, 0.4)
    
    # Now, convert the grouped top-left rectangles back to the desired center format
    final_matches = []
    for (x, y, w, h) in rectangles:
        center_x = x + w // 2
        center_y = y + h // 2
    final_results = []
    for match in all_matches:
        center_x, center_y, rW, rH, scale = match

        final_results.append([center_x - rW//2, center_y - rH//2, rW, rH, scale])

    # Re-run grouping on the list that includes scale
    rectangles_with_scale = []
    for match in final_results:
        rectangles_with_scale.append(match[0:4]) # [x, y, w, h] for grouping

    rectangles, weights = cv2.groupRectangles(rectangles_with_scale, 1, 0.4)

    output_list = []
    for (x, y, w, h) in rectangles:
        scale_approx = w / tW

        center_x = x + w // 2
        center_y = y + h // 2

        output_list.append([center_x, center_y, w, h, scale_approx])

    return np.array(output_list) if output_list else np.array([])

def find_image_on_window(hwnd, template_filepath, threshold):
    haystack_img = capture_window_by_identifier(hwnd)
    if haystack_img is None:
        return None

    template_img = cv2.imread(template_filepath, cv2.IMREAD_COLOR)
    if template_img is None:
        print(f"Error: Could not load template image at {template_filepath}")
        return None
    wX, wY, sw, sh = get_window_size(hwnd)
    h, w, _ = template_img.shape
    if h < haystack_img.shape[0]:
        result = cv2.matchTemplate(haystack_img, template_img, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val >= threshold:
            x, y = win32gui.ScreenToClient(hwnd, max_loc)
            return (wX + x, wY + y, w, h)
        else:
            return None
