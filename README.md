# 🎨 AI Paint Assistant — Your Personal MS Paint Artist 🤖🖌️

> _“Type what you imagine, and watch it come alive in MS Paint!”_

---

## 📺 Demo Video

🎥 **Watch the Demo:** [Click here to view the video](https://drive.google.com/file/d/1otglkHB4m2Ldf1523MEgGIqeSfJRIAIW/view?usp=sharing)
_(Replace with your real video URL once available — YouTube, Drive, or Loom)_

---

## 🌟 Overview

The **AI Paint Assistant** is a fully offline, intelligent drawing companion built for **Windows 10 + Python 3.10.9**.  
It listens to your natural language commands — like:

> “Draw a train with windows and track.”

And then automatically:
1. 🧠 **Understands** what you mean (via AI model trained with sentence-transformers).  
2. 🎨 **Opens MS Paint** on your PC.  
3. 🖱️ **Draws** the object live using your mouse (via `pyautogui`).  
4. 💾 **Saves** it as a PNG file.  
5. 💬 **Shows** it back to you inside a beautiful chat interface built in **Dash**.

---

## 🧩 Features

| Category | Description |
|-----------|--------------|
| 🧠 **AI Intent Understanding** | Understands text like “draw a locomotive” or “show me a flower” using a trained intent classifier (`MiniLM + LogisticRegression`). |
| 🎨 **Automated Drawing** | Opens MS Paint, sets up a blank 2000×800 canvas, centers it, and draws objects using real mouse strokes. |
| 💾 **Auto Save** | Each drawing is saved automatically to `assets/saved_drawings/` as a timestamped PNG. |
| 💬 **Chat UI** | Beautiful Dash-based chat — you can type, press Enter, and see your drawing appear as a reply with the image. |
| 🕶️ **Offline & Secure** | Fully local — no internet required after first model download. |
| 🧱 **Extensible** | Add new drawings easily — e.g., cars, airplanes, boats — by extending `paint_driver.py` and retraining the model. |

---

## 🗂️ Project Structure

```
my-project/
│
├─ app.py                       ← Dash web app (UI, callbacks, chat logic)
├─ predict.py                   ← Intent classifier (runtime)
├─ drawings.py                  ← Routes drawing commands to paint_driver
├─ paint_driver.py              ← Paint automation & geometry logic
│
├─ assets/
│   ├─ autoscroll.js            ← Frontend helper (Enter key & scroll)
│   └─ saved_drawings/          ← Saved PNG outputs
│
├─ model/
│   └─ intent_classifier.joblib ← Trained ML model (MiniLM + LogisticRegression)
│
├─ data/
│   └─ training_dataset/
│        └─ intent.csv          ← Training data for retraining the model
│
├─ model_training_code/
│   ├─ intent.py                ← Model training script
│   └─ predict.py               ← Offline test script
│
├─ chat_history.json            ← Logs chat turns and file paths
└─ requirements.txt             ← Python dependencies
```

---

## 🧠 System Architecture (Conceptual Flow)

```text
User Input  →  NLP Classifier  →  Drawing Coordinator  →  Paint Automation  →  Saved Image  →  Chat Display
     ↓              ↓                   ↓                      ↓                   ↓                   ↓
 "draw a tree" →  "tree" → perform_drawing() → pyautogui mouse strokes → tree.png → rendered in chat
```

---

## ⚙️ Installation Guide

### 🪄 Step 1 — Install Python 3.10.9
Make sure Python is on PATH:
```powershell
python --version
```
✅ Expected output:
```
Python 3.10.9
```

---

### 🧱 Step 2 — Create & Activate Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

---

### 📦 Step 3 — Install Dependencies
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

---

### 🧑‍🎨 Step 4 — Run the Application
```powershell
python app.py
```

Then open your browser at:
👉 **http://127.0.0.1:8050**

---

## 🚀 Using the App

1. Wait for MS Paint to open automatically.
2. In the chat box, type:
   ```
   draw a windmill
   ```
   or
   ```
   draw a flower
   ```
3. Press **Enter** or click **Send**.
4. Watch Paint draw live (don’t touch the mouse!).
5. The app saves the drawing → closes Paint → shows the image in chat.

🖼 All saved drawings are in:
```
assets/saved_drawings/
```

---

## 💡 Supported Drawing Commands

| Command Example | What Happens |
|-----------------|---------------|
| `draw a tree` | Draws a centered tree with trunk and leaves |
| `draw a house` | Draws a house with roof, door, and windows |
| `draw a windmill` | Draws tower + 4 blades |
| `draw a train` | Draws engine, windows, and tracks |
| `draw a star` | Draws a 5-point star |
| `draw a flower` | Draws a flower with petals, stem, and leaves |

---

## 🧰 Technical Details

| Component | Description |
|------------|--------------|
| **UI** | Dash + Bootstrap for layout, chat bubbles, auto-scroll, Enter key binding |
| **Model** | MiniLM sentence transformer + Logistic Regression trained on custom `intent.csv` |
| **Drawing Engine** | pyautogui controlling MS Paint via mouse drag actions |
| **Persistence** | chat_history.json stores user/agent turns and image paths |
| **Canvas Geometry** | Logical 2000×800 area, centered, scale factor applied for consistent sizing |

---

## ⚠️ Important Notes

- Do **not move the mouse** during drawing.
- Works **only on Windows** (uses MS Paint and Alt+Space shortcuts).
- First run will download the transformer model (~90MB).
- Each drawing session starts fresh (new Paint canvas every time).

---

## 🧩 Extending the Project

1. Add phrases + labels to `data/training_dataset/intent.csv`  
2. Retrain using:
   ```bash
   python model_training_code/intent.py
   ```
3. Add new function `draw_car_at(cx, cy, S)` inside `paint_driver.py`.
4. Map `"car"` in `perform_drawing()` in `drawings.py`.

🎉 That’s it — your AI will now draw cars too!

---

## 🖥️ Example Screenshots

| Prompt | Result |
|--------|---------|
| “draw a flower” | 🌸 ![flower](https://via.placeholder.com/200x100.png?text=flower+demo) |
| “draw a windmill” | 🌬️ ![windmill](https://via.placeholder.com/200x100.png?text=windmill+demo) |
| “draw a train” | 🚂 ![train](https://via.placeholder.com/200x100.png?text=train+demo) |

---

## 💬 Credits

Developed by **AMBIGAPATHY. S**  
Built with ❤️ using:
- [Dash](https://dash.plotly.com/)
- [SentenceTransformers](https://www.sbert.net/)
- [PyAutoGUI](https://pyautogui.readthedocs.io/)
- [Microsoft Paint 🎨]

---

## 📚 Quick Recap

| Step | Command |
|------|----------|
| 1️⃣ Create Virtual Env | `python -m venv .venv` |
| 2️⃣ Activate | `.\.venv\Scripts\activate` |
| 3️⃣ Install Deps | `pip install -r requirements.txt` |
| 4️⃣ Run App | `python app.py` |
| 5️⃣ Use URL | `http://127.0.0.1:8050` |
| 6️⃣ Type Prompt | e.g., “draw a windmill” |

---

## 🔗 Demo Video (again)

🎬 [▶ Watch full demonstration](https://drive.google.com/file/d/1otglkHB4m2Ldf1523MEgGIqeSfJRIAIW/view?usp=sharing)  

---

> 🧠💡 “AI that literally moves your mouse to paint your imagination — one stroke at a time.”  
> — *AI Paint Assistant created by AMBIGAPATHY*
