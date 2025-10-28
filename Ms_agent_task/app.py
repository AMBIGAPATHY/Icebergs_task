# app.py
import os
import json
import uuid
import datetime

import dash
from dash import Dash, html, dcc, Input, Output, State, no_update
import dash_bootstrap_components as dbc

from predict import classify_text
from drawings import perform_drawing
from paint_driver import get_saved_root

# -----------------------
# Paths / setup
# -----------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SAVED_DIR = get_saved_root()  # assets/saved_drawings from paint_driver
os.makedirs(ASSETS_DIR, exist_ok=True)
os.makedirs(SAVED_DIR, exist_ok=True)

CHAT_HISTORY_FILE = os.path.join(BASE_DIR, "chat_history.json")
APP_TITLE = "MS Paint Agent"


def _ensure_chat_history_file():
    """
    Make sure chat_history.json exists and is a JSON list.
    If invalid, reset to [].
    """
    if not os.path.exists(CHAT_HISTORY_FILE):
        with open(CHAT_HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
        return

    try:
        with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("chat_history.json not list")
    except Exception:
        with open(CHAT_HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)


def _load_chat_history():
    _ensure_chat_history_file()
    with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _append_chat_entry(user_text, predicted_label, status_text, image_web_path):
    """
    image_web_path is what <img src> will point to, e.g.
    "assets/saved_drawings/20251027_164512_flower.png"
    """
    _ensure_chat_history_file()
    with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as f:
        hist = json.load(f)

    entry = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        "user_text": user_text,
        "predicted_label": predicted_label,
        "status_text": status_text,
        "image_path": image_web_path,  # can be None
    }

    hist.append(entry)

    with open(CHAT_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(hist, f, indent=2)

    return hist


def _message_bubble(sender, text, image_src=None):
    """
    sender: "You" or "Agent"
    text: string
    image_src: optional (browser path "assets/saved_drawings/...png")
    returns a styled Div
    """
    is_user = (sender == "You")

    bubble_bg = "#334155" if is_user else "#1e293b"
    border_col = "#475569"
    header_color = "#94a3b8"

    body_children = [
        html.Div(
            sender,
            style={
                "fontWeight": 600,
                "fontSize": "0.7rem",
                "color": header_color,
                "marginBottom": "2px",
            },
        ),
        html.Div(
            text,
            style={
                "whiteSpace": "pre-wrap",
                "color": "#e2e8f0",
                "fontSize": "0.9rem",
                "lineHeight": "1.4rem",
            },
        ),
    ]

    if image_src:
        body_children.append(
            html.Img(
                src="/" + image_src.lstrip("/"),
                style={
                    "maxWidth": "260px",
                    "border": f"1px solid {border_col}",
                    "borderRadius": "6px",
                    "marginTop": "8px",
                    "backgroundColor": "#0f172a",
                },
            )
        )

    return html.Div(
        style={
            "alignSelf": "flex-start",
            "backgroundColor": bubble_bg,
            "borderRadius": "12px",
            "padding": "10px 12px",
            "maxWidth": "80%",
            "border": f"1px solid {border_col}",
            "boxShadow": "0 8px 24px rgba(0,0,0,0.4)",
        },
        children=body_children,
    )


def _chat_history_to_components(chat_items):
    """
    Render full chat log with (You -> Agent) pairs.
    """
    rows = []
    for msg in chat_items:
        user_bubble = _message_bubble("You", msg["user_text"], image_src=None)

        agent_bubble = _message_bubble(
            "Agent",
            msg["status_text"],
            image_src=msg.get("image_path"),
        )

        rows.append(
            html.Div(
                style={
                    "display": "flex",
                    "flexDirection": "column",
                    "gap": "6px",
                    "marginBottom": "20px",
                },
                children=[
                    user_bubble,
                    agent_bubble,
                ],
            )
        )
    return rows


# -----------------------
# Dash App
# -----------------------
external_stylesheets = [dbc.themes.DARKLY]
app = Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
server = app.server

app.layout = html.Div(
    style={
        "height": "100vh",
        "display": "flex",
        "flexDirection": "column",
        "backgroundColor": "#0f172a",
        "color": "#f8fafc",
        "fontFamily": "system-ui, -apple-system, BlinkMacSystemFont, 'Inter', sans-serif",
    },
    children=[

        # ----- Top Nav / Header -----
        html.Div(
            style={
                "flexShrink": 0,
                "padding": "12px 16px",
                "borderBottom": "1px solid #1e293b",
                "backgroundColor": "#0f172a",
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "space-between",
            },
            children=[
                html.Div(
                    children=[
                        html.Div(
                            APP_TITLE,
                            style={
                                "fontSize": "0.95rem",
                                "fontWeight": "600",
                                "color": "#e2e8f0",
                                "letterSpacing": "-0.03em",
                            },
                        ),
                        html.Div(
                            "Draw with pyautogui in MS Paint",
                            style={
                                "fontSize": "0.7rem",
                                "color": "#64748b",
                                "marginTop": "2px",
                            },
                        ),
                    ],
                ),
                html.Div(
                    "Chat History",
                    style={
                        "fontSize": "0.7rem",
                        "lineHeight": "1rem",
                        "color": "#475569",
                        "backgroundColor": "#1e293b",
                        "border": "1px solid #334155",
                        "borderRadius": "6px",
                        "padding": "4px 8px",
                        "fontWeight": "500",
                    },
                ),
            ],
        ),

        # ----- Chat Scroll Area -----
        html.Div(
            id="chat-scroll-wrapper",
            style={
                "flex": "1 1 auto",
                "overflowY": "auto",
                "backgroundColor": "#0f172a",
                "padding": "16px",
                "display": "flex",
                "flexDirection": "column",
            },
            children=_chat_history_to_components(_load_chat_history()),
        ),

        # Divider line above input
        html.Div(
            style={
                "flexShrink": 0,
                "height": "1px",
                "background": "linear-gradient(to right, rgba(51,65,85,0), #334155 20%, #334155 80%, rgba(51,65,85,0))",
            }
        ),

        # ----- Bottom Input Bar -----
        html.Div(
            style={
                "flexShrink": 0,
                "padding": "12px 16px",
                "backgroundColor": "#0f172a",
                "display": "flex",
                "gap": "8px",
                "alignItems": "center",
            },
            children=[
                dcc.Input(
                    id="user-input",
                    type="text",
                    placeholder="Ask me to draw something... try 'draw a flower'",
                    style={
                        "flex": "1 1 auto",
                        "backgroundColor": "#1e293b",
                        "border": "1px solid #334155",
                        "borderRadius": "10px",
                        "padding": "12px 14px",
                        "color": "#e2e8f0",
                        "fontSize": "0.9rem",
                        "lineHeight": "1.2rem",
                        "outline": "none",
                        "width": "100%",
                        "boxShadow": "0 8px 24px rgba(0,0,0,0.6)",
                    },
                    # n_submit will fire on Enter (we'll capture this in JS -> clicks Send)
                    n_submit=0,
                ),
                html.Button(
                    "Send",
                    id="send-btn",
                    n_clicks=0,
                    style={
                        "backgroundColor": "#3b82f6",
                        "color": "#fff",
                        "border": "0",
                        "borderRadius": "10px",
                        "fontSize": "0.9rem",
                        "fontWeight": "600",
                        "padding": "12px 16px",
                        "cursor": "pointer",
                        "lineHeight": "1rem",
                        "whiteSpace": "nowrap",
                        "boxShadow": "0 12px 32px rgba(59,130,246,0.4)",
                    },
                ),
            ],
        ),

        # ----- hidden stores / triggers -----
        dcc.Store(id="scroll-token", data=str(uuid.uuid4())),
        # we need a dummy output for clientside scroll callback
        dcc.Store(id="scroll-dummy"),
    ],
)

# ---------------------------------
# Clientside callbacks (JS in browser)
# ---------------------------------

# 1. Auto-scroll to bottom when scroll-token changes
app.clientside_callback(
    """
    function(token) {
        try {
            const wrap = document.getElementById("chat-scroll-wrapper");
            if (wrap) {
                wrap.scrollTop = wrap.scrollHeight;
            }
        } catch (e) {
            console.warn("scrollChat error", e);
        }
        return null;
    }
    """,
    Output("scroll-dummy", "data"),
    Input("scroll-token", "data"),
)

# 2. Make Enter trigger the Send button click reliably.
# We'll listen for n_submit in Python side, BUT we'll also
# add JS in assets/autoscroll.js to synthesize a click.
# However, to keep the logic simple and single-source-of-truth:
# We'll ONLY trigger off Send button in Python callback.
#
# The JS will "click" the real button when Enter is pressed.
#
# So our Python callback only depends on send-btn.n_clicks
# and reads user-input.value.
#
# That means:
#   - clicking Send => n_clicks++
#   - pressing Enter => JS does sendBtn.click() => same effect.
#
# Result: exactly one path, no duplication.


# ---------------------------------
# Server callback for sending messages
# ---------------------------------
@app.callback(
    Output("chat-scroll-wrapper", "children"),
    Output("user-input", "value"),
    Output("scroll-token", "data"),
    Input("send-btn", "n_clicks"),
    State("user-input", "value"),
    prevent_initial_call=True,
)
def handle_user_message(n_clicks, user_text):
    """
    Triggered by clicking Send
    (or by JS simulating a click on Enter keypress).

    Flow:
    1. classify user text
    2. if known -> perform_drawing() => PNG path
    3. else -> fallback
    4. append to chat_history.json
    5. redraw UI, clear input, update scroll-token
    """

    # Dash calls this whenever n_clicks changes. If no text or blank, ignore.
    if not user_text or user_text.strip() == "":
        raise dash.exceptions.PreventUpdate

    user_msg = user_text.strip()

    # classification
    predicted_label = classify_text(user_msg)  # e.g. "tree", "flower", or "unknown"

    # known shape => draw with pyautogui
    if predicted_label != "unknown":
        abs_png_path = perform_drawing(predicted_label)
        if abs_png_path:
            # assets/saved_drawings/...png relative path for browser
            rel_from_base = os.path.relpath(abs_png_path, BASE_DIR).replace("\\", "/")
            image_web_path = rel_from_base  # "assets/saved_drawings/xxx.png"
            status_text = f"Here is your {predicted_label}!"
        else:
            image_web_path = None
            status_text = (
                f"I tried to draw '{predicted_label}', "
                "but something went wrong while using Paint."
            )
    else:
        image_web_path = None
        status_text = (
            "I don't know that drawing yet.\n"
            "I can do things like tree, house, windmill, train, star, flower."
        )

    # persist in chat_history.json
    full_history = _append_chat_entry(
        user_text=user_msg,
        predicted_label=predicted_label,
        status_text=status_text,
        image_web_path=image_web_path,
    )

    # update chat UI
    chat_children = _chat_history_to_components(full_history)

    # clear input + trigger scroll
    return chat_children, "", str(uuid.uuid4())


if __name__ == "__main__":
    # by default Dash serves /assets automatically
    app.run_server(host="0.0.0.0", port=8050, debug=False)
