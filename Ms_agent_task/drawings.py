# drawings.py
import os
import datetime
import time

from paint_driver import (
    open_paint_and_prepare,
    save_and_close_paint,
    draw_tree_at,
    draw_house_at,
    draw_windmill_at,
    draw_train_at,
    draw_star_at,
    draw_flower_at,
    get_scale_fn,
    get_saved_root,
)

def _timestamp():
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

def perform_drawing(label: str):
    """
    1. open Paint session (new canvas, centered)
    2. draw shape based on label
    3. save final PNG in assets/saved_drawings/<timestamp>_<label>.png
    4. return that absolute path
    """
    ok, cx, cy, session_name, first_filepath = open_paint_and_prepare()
    if not ok:
        return None

    S = get_scale_fn()
    shape_key = (label or "").strip().lower()

    if shape_key == "tree":
        draw_tree_at(cx, cy, S)
    elif shape_key == "house":
        draw_house_at(cx, cy, S)
    elif shape_key == "windmill":
        draw_windmill_at(cx, cy, S)
    elif shape_key == "train":
        draw_train_at(cx, cy, S)
    elif shape_key == "star":
        draw_star_at(cx, cy, S)
    elif shape_key == "flower":
        draw_flower_at(cx, cy, S)
    else:
        # unknown: still close paint but don't produce final custom filename
        save_and_close_paint(first_filepath)
        return None

    time.sleep(0.5)

    final_filename = f"{_timestamp()}_{shape_key}.png"
    final_abs_path = os.path.join(get_saved_root(), final_filename)

    save_and_close_paint(final_abs_path)

    return final_abs_path
