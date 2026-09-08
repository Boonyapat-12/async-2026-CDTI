# 🚜 Tank Battle Multiplayer Game

A real-time, asynchronous multiplayer tank battle game powered by **Python (asyncio)**, **Redis Pub/Sub**, **FastAPI (WebSockets)**, and **HTML5 Canvas**.

---

## 1. Installation

Before running the project, ensure that a **Redis Server** is installed and running on your machine (Default host/port: `localhost:6379`).

Next, install the required Python dependencies via `pip`:

```bash
# Dependencies for Server, Dashboard, and Web Dashboard
pip install fastapi uvicorn redis websocket

# Dependencies for Player Controllers (Human Tank) and AI Bots
pip install pynput redis

```

---

## 2. How to Play

Open separate terminal windows/tabs for each component and run them in the following order:

### **Step 1: Start the Game Server**

Launch the central game server that manages physics, collisions, and rules.

```bash
python server.py

```

*(Upon launch, the Server will enter the `WAITING` state, listening for incoming player registrations.)*

---

### **Step 2: Start the Dashboard**

Choose one (or both) of the visual dashboards to monitor gameplay in real time:

* **Option A: Web Dashboard (Recommended for Multiplayer)**
```bash
python web_dashboard.py

```


Open your web browser and navigate to: `http://localhost:8000`
* **Option B: Terminal Dashboard**
```bash
python dashboard.py

```



---

### **Step 3: Join the Game (Players / Bots)**

Spawn as many human players or AI bots as desired:

* **To control a tank manually (Human Player):**
```bash
python tank.py Player_1

```


* ⬆️ ⬇️ ⬅️ ➡️ : Move / Rotate Turret
* `Spacebar` : Fire Shell (`FIRE`)


* **To spawn an AI Bot player:**
```bash
python bot.py Bot_1

```


*(You can open additional terminal tabs to run `bot.py Bot_2`, `bot.py Bot_3`, etc.)*

---

### **Step 4: Start the Match**

Switch back to the terminal window running **`server.py`** and press **`[ENTER]`** to start the game!

---

## 3. Restarting the Game

When a match ends (`GAME_OVER`), you can restart the game without restarting the individual client scripts:

1. Press `[ENTER]` in the `server.py` terminal window to reset the state back to `WAITING`.
2. All existing clients (`tank.py` and `bot.py`) will automatically **re-register** with the server.
3. Once all players are re-registered and ready, press `[ENTER]` again in `server.py**` to start the new match.
