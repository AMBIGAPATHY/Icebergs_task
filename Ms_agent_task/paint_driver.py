# paint_driver.py
import os
import time
import math
import datetime
import subprocess
import pyautogui

# ---------- timing controls ----------
SLOW_FACTOR = float(os.environ.get("PAINT_SLOW", "1.0"))
BASE_SHORT = 0.12
BASE_MED   = 0.30
BASE_LONG  = 0.60

def _sleep_short(): time.sleep(BASE_SHORT * SLOW_FACTOR)
def _sleep_med():   time.sleep(BASE_MED   * SLOW_FACTOR)
def _sleep_long():  time.sleep(BASE_LONG  * SLOW_FACTOR)

pyautogui.FAILSAFE = (os.environ.get("PAINT_FAILSAFE", "1") != "0")
pyautogui.PAUSE = float(os.environ.get("PAINT_PAUSE", "0.05")) * SLOW_FACTOR

# ---------- paths / canvas ----------
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SAVED_ROOT = os.path.join(ASSETS_DIR, "saved_drawings")
os.makedirs(SAVED_ROOT, exist_ok=True)

CANVAS_W = 2000
CANVAS_H = 800

def _new_session_name():
    stamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"draw-{stamp}"

def _session_filepath(session_name: str):
    return os.path.join(SAVED_ROOT, f"{session_name}.png")


# ---------- paint control ----------
def _launch_paint_process():
    try:
        subprocess.Popen(["mspaint"])
    except FileNotFoundError:
        raise RuntimeError("MS Paint not found. Must run on Windows.")
    except Exception as e:
        raise RuntimeError(f"Failed to launch Paint: {e}")

def _sleep_for_paint_boot():
    _sleep_long()
    _sleep_long()

def _activate_paint_window_for_session(session_name: str) -> bool:
    try:
        titles_to_check = [
            f"{session_name}.png - Paint",
            f"{session_name} - Paint",
            "Paint",
        ]
        for t in titles_to_check:
            wins = pyautogui.getWindowsWithTitle(t)
            if not wins:
                continue
            w = wins[0]
            try:
                if hasattr(w, "isMinimized") and w.isMinimized:
                    w.restore()
                    _sleep_med()
                w.activate()
                _sleep_med()
                return True
            except Exception:
                pass
    except Exception:
        pass
    return False

def _maximize_window():
    try:
        pyautogui.hotkey('alt', 'space')
        _sleep_med()
        pyautogui.press('x')
        _sleep_med()
    except Exception:
        pass

def _normalize_zoom():
    try:
        pyautogui.hotkey('ctrl', '1')
        _sleep_med()
    except Exception:
        pass

def _set_canvas_size(width_px=CANVAS_W, height_px=CANVAS_H):
    try:
        pyautogui.hotkey('ctrl', 'e')
        _sleep_long()
        try:
            pyautogui.hotkey('alt', 'p')
            _sleep_short()
        except Exception:
            pass

        pyautogui.typewrite(str(width_px))
        _sleep_short()
        pyautogui.press('tab')
        _sleep_short()
        pyautogui.typewrite(str(height_px))
        _sleep_short()
        pyautogui.press('enter')
        _sleep_long()
    except Exception as e:
        print("Canvas resize failed:", e)

def _save_as(filepath: str):
    try:
        pyautogui.press('f12')
        _sleep_long()
        pyautogui.typewrite(filepath)
        _sleep_short()
        pyautogui.press('enter')
        _sleep_long()
        pyautogui.press('enter')  # confirm format popup
        _sleep_med()
    except Exception as e:
        print("Save As failed:", e)

def _save():
    try:
        pyautogui.hotkey('ctrl', 's')
        _sleep_med()
    except Exception:
        pass

def _close_paint():
    try:
        pyautogui.hotkey('alt', 'f4')
        _sleep_med()
        pyautogui.press('n')  # don't save changes again
    except Exception:
        pass

def _force_brush_tool():
    try:
        pyautogui.hotkey('alt', 'b')
        _sleep_med()
    except Exception:
        pass

def _get_canvas_center():
    screen_w, screen_h = pyautogui.size()
    canvas_left = (screen_w - CANVAS_W) // 2
    canvas_top  = (screen_h - CANVAS_H) // 2
    cx = canvas_left + CANVAS_W // 2
    cy = canvas_top  + CANVAS_H // 2
    return cx, cy

def _scale_medium_large():
    scale = 1.2
    def S(x):
        return int(round(x * scale))
    return S

def open_paint_and_prepare():
    session_name = _new_session_name()
    filepath     = _session_filepath(session_name)

    _launch_paint_process()
    _sleep_for_paint_boot()

    _activate_paint_window_for_session(session_name)
    _maximize_window()
    _normalize_zoom()
    _set_canvas_size(CANVAS_W, CANVAS_H)

    _save_as(filepath)

    _activate_paint_window_for_session(session_name)
    _force_brush_tool()

    cx, cy = _get_canvas_center()
    return True, cx, cy, session_name, filepath


# ---------- primitive helpers ----------
def _rect_outline_thick(x1, y1, x2, y2, repeat=4, dur=0.01):
    left   = min(x1, x2)
    right  = max(x1, x2)
    top    = min(y1, y2)
    bottom = max(y1, y2)

    for _ in range(repeat):
        pyautogui.moveTo(left, bottom)
        pyautogui.dragTo(right, bottom, duration=dur, button='left')
        pyautogui.dragTo(right, top,    duration=dur, button='left')
        pyautogui.dragTo(left,  top,    duration=dur, button='left')
        pyautogui.dragTo(left,  bottom, duration=dur, button='left')

def _stroke_line(x1, y1, x2, y2, repeat=1, dur=0.05):
    for _ in range(repeat):
        pyautogui.moveTo(x1, y1)
        pyautogui.dragTo(x2, y2, duration=dur, button='left')

def _circle(cx, cy, r, dur=0.01, steps=24):
    for i in range(steps + 1):
        ang = 2 * math.pi * i / steps
        x = int(cx + r * math.cos(ang))
        y = int(cy + r * math.sin(ang))
        if i == 0:
            pyautogui.moveTo(x, y)
        else:
            pyautogui.dragTo(x, y, duration=dur, button='left')


# ---------- SHAPES ----------
def draw_tree_at(cx, cy, S):
    trunk_w = S(30)
    trunk_h = S(100)
    leaf_base = S(170)
    layers = 3
    layer_gap = S(60)

    bottom_y = cy + (trunk_h + S(80) + (layers - 1) * layer_gap) // 2
    trunk_x = cx - trunk_w // 2
    trunk_y = bottom_y

    pyautogui.moveTo(trunk_x, trunk_y)
    pyautogui.dragRel(0, -trunk_h, duration=0.22, button='left')
    pyautogui.dragRel(trunk_w, 0, duration=0.22, button='left')
    pyautogui.dragRel(0,  trunk_h, duration=0.22, button='left')
    pyautogui.dragRel(-trunk_w, 0, duration=0.22, button='left')

    leaf_start_y = trunk_y - trunk_h
    for i in range(layers):
        layer_base = leaf_base - S(20) * i
        layer_height = S(80)
        layer_x_start = cx - layer_base // 2
        layer_y_start = leaf_start_y - layer_gap * i

        pyautogui.moveTo(layer_x_start, layer_y_start)
        pyautogui.dragRel(layer_base // 2, -layer_height, duration=0.22, button='left')
        pyautogui.dragRel(layer_base // 2,  layer_height, duration=0.22, button='left')
        pyautogui.dragRel(-layer_base,      0,           duration=0.22, button='left')

def draw_windmill_at(cx, cy, S):
    tower_w_bottom = S(60)
    tower_w_top    = S(30)
    tower_h        = S(180)
    hub_r          = S(15)
    blade_len      = S(80)
    blade_w        = S(15)

    tower_bottom_y = cy + tower_h // 2
    tower_top_y    = tower_bottom_y - tower_h

    left_bottom_x  = cx - tower_w_bottom // 2
    right_bottom_x = cx + tower_w_bottom // 2
    left_top_x     = cx - tower_w_top // 2
    right_top_x    = cx + tower_w_top // 2

    pyautogui.moveTo(left_bottom_x, tower_bottom_y)
    pyautogui.dragTo(right_bottom_x, tower_bottom_y, duration=0.15, button='left')
    pyautogui.dragTo(right_top_x, tower_top_y, duration=0.15, button='left')
    pyautogui.dragTo(left_top_x, tower_top_y, duration=0.15, button='left')
    pyautogui.dragTo(left_bottom_x, tower_bottom_y, duration=0.15, button='left')

    hub_cx = cx
    hub_cy = tower_top_y
    steps = 24
    for i in range(steps + 1):
        ang = 2 * math.pi * i / steps
        x = int(hub_cx + hub_r * math.cos(ang))
        y = int(hub_cy + hub_r * math.sin(ang))
        if i == 0:
            pyautogui.moveTo(x, y)
        else:
            pyautogui.dragTo(x, y, duration=0.01, button='left')

    def _blade(dx, dy):
        end_x = hub_cx + dx * blade_len
        end_y = hub_cy + dy * blade_len
        px = -dy
        py = dx
        half_w = blade_w / 2.0

        p1 = (hub_cx + px * half_w, hub_cy + py * half_w)
        p2 = (end_x + px * half_w,  end_y + py * half_w)
        p3 = (end_x - px * half_w,  end_y - py * half_w)
        p4 = (hub_cx - px * half_w, hub_cy - py * half_w)

        pts = [p1, p2, p3, p4, p1]
        x0, y0 = int(pts[0][0]), int(pts[0][1])
        pyautogui.moveTo(x0, y0)
        for (xx, yy) in pts[1:]:
            pyautogui.dragTo(int(xx), int(yy), duration=0.05, button='left')

    _blade(0, -1)
    _blade(1, 0)
    _blade(0, 1)
    _blade(-1, 0)

def draw_flower_at(cx, cy, S):
    center_radius = S(20)
    steps = 36

    for i in range(steps):
        ang = 2 * math.pi * i / steps
        x = int(cx + center_radius * math.cos(ang))
        y = int(cy + center_radius * math.sin(ang))
        if i == 0:
            pyautogui.moveTo(x, y)
        else:
            pyautogui.dragTo(x, y, duration=0.012, button='left')

    petal_radius = S(30)
    num_petals = 8
    for i in range(num_petals):
        angle_offset = 2 * math.pi * i / num_petals
        pcx = int(cx + (center_radius + petal_radius) * math.cos(angle_offset))
        pcy = int(cy + (center_radius + petal_radius) * math.sin(angle_offset))
        for j in range(steps):
            ang = 2 * math.pi * j / steps
            x = int(pcx + petal_radius * math.cos(ang))
            y = int(pcy + petal_radius * math.sin(ang))
            if j == 0:
                pyautogui.moveTo(x, y)
            else:
                pyautogui.dragTo(x, y, duration=0.012, button='left')

    stem_height = S(100)
    stem_x = cx
    stem_y_start = cy + center_radius + petal_radius
    pyautogui.moveTo(stem_x, stem_y_start)
    pyautogui.dragRel(0, stem_height, duration=0.26, button='left')

    leaf_size = S(40)
    pyautogui.moveTo(stem_x, stem_y_start + S(20))
    pyautogui.dragRel(-leaf_size, leaf_size // 2, duration=0.12, button='left')
    pyautogui.dragRel(leaf_size, 0, duration=0.12, button='left')
    pyautogui.dragRel(-leaf_size, -leaf_size // 2, duration=0.12, button='left')

    pyautogui.moveTo(stem_x, stem_y_start + S(60))
    pyautogui.dragRel(leaf_size, leaf_size // 2, duration=0.12, button='left')
    pyautogui.dragRel(-leaf_size, 0, duration=0.12, button='left')
    pyautogui.dragRel(leaf_size, -leaf_size // 2, duration=0.12, button='left')

def draw_star_at(cx, cy, S):
    outer_r = S(100)
    inner_r = S(40)
    pts = []
    for i in range(10):
        angle_deg = 90 + i * 36
        angle = math.radians(angle_deg)
        r = outer_r if i % 2 == 0 else inner_r
        x = int(cx + r * math.cos(angle))
        y = int(cy - r * math.sin(angle))
        pts.append((x, y))

    pyautogui.moveTo(pts[0])
    for p in pts[1:]:
        pyautogui.dragTo(p, duration=0.05, button='left')
    pyautogui.dragTo(pts[0], duration=0.05, button='left')

def draw_train_at(cx, cy, S):
    engine_w   = S(150)
    engine_h   = S(80)
    car_w      = S(120)
    car_h      = S(70)
    gap        = S(30)

    wheel_r    = S(20)
    roof_h     = S(30)
    stack_w    = S(15)
    stack_h    = S(30)

    base_y = cy + engine_h // 2

    engine_left_x  = cx - (engine_w // 2) - (car_w // 2) - (gap // 2)
    engine_right_x = engine_left_x + engine_w
    engine_top_y   = base_y - engine_h

    car_left_x     = engine_right_x + gap
    car_right_x    = car_left_x + car_w
    car_top_y      = base_y - car_h

    def _rect(x1, y1, x2, y2, dur=0.12):
        left   = min(x1, x2)
        right  = max(x1, x2)
        top    = min(y1, y2)
        bottom = max(y1, y2)

        pyautogui.moveTo(left, bottom)
        pyautogui.dragTo(right, bottom, duration=dur, button="left")
        pyautogui.dragTo(right, top,    duration=dur, button="left")
        pyautogui.dragTo(left,  top,    duration=dur, button="left")
        pyautogui.dragTo(left,  bottom, duration=dur, button="left")

    def _circle_local(cx0, cy0, r, dur=0.01, steps=24):
        for i in range(steps + 1):
            ang = 2 * math.pi * i / steps
            x = int(cx0 + r * math.cos(ang))
            y = int(cy0 + r * math.sin(ang))
            if i == 0:
                pyautogui.moveTo(x, y)
            else:
                pyautogui.dragTo(x, y, duration=dur, button="left")

    # engine body
    _rect(engine_left_x, base_y, engine_right_x, engine_top_y, dur=0.15)

    # cab
    cab_w = int(engine_w * 0.5)
    cab_left_x = engine_right_x - cab_w
    cab_top_y  = engine_top_y - roof_h
    _rect(cab_left_x, engine_top_y, engine_right_x, cab_top_y, dur=0.12)

    # smokestack
    stack_left_x  = engine_left_x + S(20)
    stack_right_x = stack_left_x + stack_w
    stack_top_y   = engine_top_y - stack_h
    _rect(stack_left_x, engine_top_y, stack_right_x, stack_top_y, dur=0.10)

    # cowcatcher triangle
    cow_len = S(30)
    nose_base_x  = engine_left_x
    nose_base_y  = base_y
    pyautogui.moveTo(nose_base_x, nose_base_y)
    pyautogui.dragRel(-cow_len,  S(20), duration=0.12, button="left")
    pyautogui.dragRel(0,        -S(40), duration=0.12, button="left")
    pyautogui.dragRel(cow_len,   S(20), duration=0.12, button="left")

    # windows in cab
    win_w  = S(25)
    win_h  = S(20)
    win_gap = S(8)
    first_win_left_x  = cab_left_x + S(10)
    first_win_right_x = first_win_left_x + win_w
    first_win_top_y   = cab_top_y + S(10)
    first_win_bottom_y= first_win_top_y + win_h

    second_win_left_x  = first_win_right_x + win_gap
    second_win_right_x = second_win_left_x + win_w
    second_win_top_y   = first_win_top_y
    second_win_bottom_y= first_win_bottom_y

    _rect(first_win_left_x, first_win_bottom_y,
          first_win_right_x, first_win_top_y, dur=0.08)
    _rect(second_win_left_x, second_win_bottom_y,
          second_win_right_x, second_win_top_y, dur=0.08)

    # boxcar
    _rect(car_left_x, base_y, car_right_x, car_top_y, dur=0.15)

    # boxcar windows
    car_win_size = S(18)
    car_win_gap  = S(12)
    first_car_win_left_x = car_left_x + S(15)
    car_win_top_y        = car_top_y + S(15)
    car_win_bottom_y     = car_win_top_y + car_win_size

    for w_i in range(3):
        lx = first_car_win_left_x + w_i * (car_win_size + car_win_gap)
        rx = lx + car_win_size
        _rect(lx, car_win_bottom_y, rx, car_win_top_y, dur=0.08)

    # connector bar
    connector_y = base_y - S(20)
    _stroke_line(engine_right_x, connector_y, car_left_x, connector_y, repeat=1, dur=0.12)

    # wheels
    engine_wheel_offsets = [S(40), S(100)]
    for off in engine_wheel_offsets:
        wx = engine_left_x + off
        wy = base_y + wheel_r
        _circle_local(wx, wy, wheel_r, dur=0.01, steps=24)

    car_wheel_offsets = [S(30), S(90)]
    for off in car_wheel_offsets:
        wx = car_left_x + off
        wy = base_y + wheel_r
        _circle_local(wx, wy, wheel_r, dur=0.01, steps=24)

    # track rails
    rail_left_x  = engine_left_x - S(40)
    rail_right_x = car_right_x + S(40)
    track_top_y    = base_y + wheel_r + S(10)
    track_bottom_y = track_top_y + S(8)

    _stroke_line(rail_left_x,  track_top_y,    rail_right_x, track_top_y,    repeat=1, dur=0.20)
    _stroke_line(rail_left_x,  track_bottom_y, rail_right_x, track_bottom_y, repeat=1, dur=0.20)

    sleeper_height = S(10)
    sleeper_width  = S(25)
    sleeper_gap    = S(30)
    sleeper_y_top    = track_top_y
    sleeper_y_bottom = track_bottom_y + sleeper_height

    x_cursor = rail_left_x
    while x_cursor <= rail_right_x:
        _rect(x_cursor, sleeper_y_bottom, x_cursor + sleeper_width, sleeper_y_top, dur=0.06)
        x_cursor += sleeper_gap

def draw_house_at(cx, cy, S):
    body_w = S(280)
    body_h = S(90)
    roof_h = S(70)
    overhang = S(30)
    base_h = S(14)

    door_w = S(60)
    door_h = S(60)
    door_inset = S(25)
    knob_dx = S(38)
    knob_dy = S(32)
    knob_r  = S(3)

    win_w = S(80)
    win_h = S(40)
    win_inset_right = S(35)
    win_offset_down = S(20)
    win_inner_pad   = S(6)

    wall_left  = cx - body_w // 2
    wall_right = cx + body_w // 2
    wall_top   = cy - body_h // 2
    wall_bot   = cy + body_h // 2

    ground_top = wall_bot
    ground_bot = wall_bot + base_h

    peak_x = wall_left + S(120)
    peak_y = wall_top - roof_h
    roof_left_x  = wall_left - overhang
    roof_left_y  = wall_top
    roof_right_x = wall_right + overhang
    roof_right_y = wall_top

    divider_x = (wall_left + wall_right) // 2
    divider_top_y = wall_top
    divider_bot_y = wall_bot

    diag_start_x = peak_x
    diag_start_y = peak_y
    diag_end_x   = divider_x
    diag_end_y   = wall_top

    door_left  = wall_left + door_inset
    door_right = door_left + door_w
    door_bot   = wall_bot
    door_top   = door_bot - door_h

    win_right = wall_right - win_inset_right
    win_left  = win_right - win_w
    win_top   = wall_top + win_offset_down
    win_bot   = win_top + win_h

    def _stroke_line_thick(x1, y1, x2, y2, repeat=4, dur=0.01):
        for _ in range(repeat):
            pyautogui.moveTo(x1, y1)
            pyautogui.dragTo(x2, y2, duration=dur, button="left")

    def _tiny_square(xc, yc, r, repeat=3):
        for _ in range(repeat):
            pyautogui.moveTo(xc-r, yc-r)
            pyautogui.dragTo(xc+r, yc-r, duration=0.01, button="left")
            pyautogui.dragTo(xc+r, yc+r, duration=0.01, button="left")
            pyautogui.dragTo(xc-r, yc+r, duration=0.01, button="left")
            pyautogui.dragTo(xc-r, yc-r, duration=0.01, button="left")

    _rect_outline_thick(wall_left, wall_top, wall_right, wall_bot, repeat=4)

    _rect_outline_thick(wall_left, ground_top, wall_right, ground_bot, repeat=4)
    _stroke_line_thick(wall_left, ground_top, wall_right, ground_top, repeat=2)
    _stroke_line_thick(wall_left, ground_bot, wall_right, ground_bot, repeat=2)

    _stroke_line_thick(roof_left_x,  roof_left_y,  peak_x,      peak_y,      repeat=4)
    _stroke_line_thick(peak_x,       peak_y,       roof_right_x,roof_right_y,repeat=4)
    _stroke_line_thick(roof_left_x,  roof_left_y,  roof_right_x,roof_right_y,repeat=4)

    _stroke_line_thick(diag_start_x, diag_start_y, diag_end_x,   diag_end_y,   repeat=4)
    _stroke_line_thick(divider_x,    divider_top_y,divider_x,    divider_bot_y,repeat=4)

    _rect_outline_thick(door_left, door_top, door_right, door_bot, repeat=4)
    door_mid_x = (door_left + door_right) // 2
    _stroke_line_thick(door_mid_x, door_top, door_mid_x, door_bot, repeat=4)

    knob_x = door_left + knob_dx
    knob_y = door_top + knob_dy
    _tiny_square(knob_x, knob_y, knob_r, repeat=3)

    _rect_outline_thick(win_left, win_top, win_right, win_bot, repeat=4)

    innerL = win_left  + win_inner_pad
    innerR = win_right - win_inner_pad
    innerT = win_top   + win_inner_pad
    innerB = win_bot   - win_inner_pad
    _rect_outline_thick(innerL, innerT, innerR, innerB, repeat=2)


def save_and_close_paint(final_filepath: str):
    """
    Save final image into assets/saved_drawings/<...>.png, then close Paint.
    """
    _save()
    _sleep_med()

    pyautogui.press('f12')
    _sleep_med()
    pyautogui.typewrite(final_filepath)
    _sleep_short()
    pyautogui.press('enter')
    _sleep_long()
    pyautogui.press('enter')
    _sleep_med()

    _close_paint()
    _sleep_med()


def get_scale_fn():
    return _scale_medium_large()

def get_saved_root():
    return SAVED_ROOT
