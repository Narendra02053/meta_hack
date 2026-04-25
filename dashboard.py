import streamlit as st
import time
import json
import matplotlib.pyplot as plt
import os
import pandas as pd

from warehouse_env import WarehouseEnv

# Page configuration
st.set_page_config(
    page_title="Warehouse AI | Elite Multi-Agent Command",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 4. Prevent Layout Jumping & Premium Aesthetics
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    section.main > div {
        padding-top: 1rem;
    }
    
    .stApp {
        background: radial-gradient(circle at top right, #1e293b, #0f172a);
        color: #f8fafc;
    }
    
    h1, h2, h3 {
        color: #38bdf8 !important;
        font-weight: 800 !important;
        letter-spacing: -0.025em;
        text-transform: uppercase;
    }
    
    .stMetric {
        background: rgba(30, 41, 59, 0.6);
        backdrop-filter: blur(12px);
        padding: 1.5rem;
        border-radius: 1.25rem;
        border: 1px solid rgba(56, 189, 248, 0.3);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%);
        color: white;
        border: none;
        padding: 0.75rem 1rem;
        border-radius: 0.75rem;
        font-weight: 700;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 20px 25px -5px rgba(37, 99, 235, 0.4);
        background: linear-gradient(135deg, #38bdf8 0%, #3b82f6 100%);
    }

    .grid-cell {
        transition: all 0.3s ease;
    }
    .grid-cell:hover {
        background: rgba(56, 189, 248, 0.1) !important;
        transform: scale(1.05);
    }
</style>
""", unsafe_allow_html=True)

# 1. Implement Persistent Simulation State
if "env" not in st.session_state:
    st.session_state.env = WarehouseEnv()

env = st.session_state.env

if "state" not in st.session_state:
    st.session_state.state = env.get_state()

if "total_reward" not in st.session_state:
    st.session_state.total_reward = 0

def save_episode_data():
    summary = env.get_summary()
    with open("episode_summary.json", "w") as f:
        json.dump(summary, f, indent=4)
    
    with open("episode_history.json", "w") as f:
        json.dump(env.episode_history, f, indent=4)

def run_replay():
    if not os.path.exists("episode_history.json"):
        st.sidebar.error("No history found.")
        return
    
    with open("episode_history.json", "r") as f:
        history = json.load(f)
    
    replay_placeholder = st.empty()
    status_placeholder = st.sidebar.empty()
    
    for i, step_data in enumerate(history):
        status_placeholder.info(f"Replaying Step {i+1}/{len(history)} (Robot {step_data['robot_id']+1}: {step_data['action']})")
        
        # We need a temporary mock env object to reuse render_grid
        class MockEnv:
            def __init__(self, state):
                self.state = state
                self.grid_size = (5, 5)
                self.charging_stations = [(0, 0), (4, 4)]
                self.obstacles = state.get("obstacles", [])
            def get_state(self): return self.state
            
        mock_env = MockEnv(step_data["state"])
        replay_placeholder.markdown(render_grid(mock_env), unsafe_allow_html=True)
        time.sleep(0.3)
    
    status_placeholder.success("Replay Complete!")
    time.sleep(2)
    status_placeholder.empty()
    st.rerun()

# Header Section
st.title("🏗️ Elite Warehouse Multi-Agent Command")
st.markdown("<p style='color: #94a3b8; font-size: 1.1rem; margin-top: -1rem;'>Autonomous Logistics Optimization Engine v2.5</p>", unsafe_allow_html=True)

# Metrics Section
completed_tasks = sum(1 for t in st.session_state.state["tasks"] if t["completed"])
total_tasks = len(st.session_state.state["tasks"])
avg_battery = sum(r["battery"] for r in st.session_state.state["robots"]) / len(st.session_state.state["robots"])

# Performance Rating Logic (Targeting 90+)
perf_rating = 0
if env.step_count > 0:
    # Weighted score: Tasks completion (70%) + Efficiency (30%)
    success_rate = (completed_tasks / total_tasks) * 100
    efficiency = min(1.0, (completed_tasks / env.step_count) * 5) # Normalized efficiency
    perf_rating = int((success_rate * 0.7) + (efficiency * 30))

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Task Success", f"{completed_tasks}/{total_tasks}", delta=f"{int((completed_tasks/total_tasks)*100)}%")
m2.metric("Fleet Status", f"{avg_battery:.0f}%", delta="Charging" if avg_battery < 30 else "Optimal", delta_color="normal")
m3.metric("System Rating", f"{perf_rating}%", delta="Elite" if perf_rating >= 90 else "Analyzing")
m4.metric("🤝 Coordination", f"{st.session_state.state.get('coordination_score', 0)}")
m5.metric("Total Reward", f"{st.session_state.total_reward}")

# 1. Create Fixed Layout Columns Once
col_grid, col_chart = st.columns([1.8, 1.2])

# Persistent Containers
grid_section = col_grid.container()
telemetry_section = col_grid.container()
task_section = col_grid.container()
chart_container = col_chart.container()
event_section = col_chart.container()

# --- UI Layout Preparation ---
st.sidebar.header("🕹️ Mission Control")

# Reset Logic
if st.sidebar.button("🔄 Full System Reset"):
    if st.session_state.env.step_count > 0:
        history_file = "reward_history.json"
        history = []
        if os.path.exists(history_file):
            with open(history_file, "r") as f:
                try: history = json.load(f)
                except: history = []
        history.append(st.session_state.total_reward)
        with open(history_file, "w") as f:
            json.dump(history, f)
            
    save_episode_data()
    st.session_state.env = WarehouseEnv()
    st.session_state.state = st.session_state.env.get_state()
    st.session_state.total_reward = 0
    st.rerun()

st.sidebar.markdown("---")
# Action Controls
if st.sidebar.button("▶️ Execute Next Phase"):
    for robot_id in range(len(env.robots)):
        action = env.intelligent_action(robot_id)
        state, reward, done = env.step(robot_id, action)
        st.session_state.total_reward += reward
    st.session_state.state = env.get_state()

if st.sidebar.button("⏭️ Auto-Simulate (10 Phases)"):
    for _ in range(10):
        sim_done = False
        for robot_id in range(len(env.robots)):
            action = env.intelligent_action(robot_id)
            state, reward, done = env.step(robot_id, action)
            st.session_state.total_reward += reward
            if done:
                sim_done = True
                break
        if sim_done:
            save_episode_data()
            break
        time.sleep(0.1)
    st.session_state.state = env.get_state()

if st.sidebar.button("📦 Emergency Task Injection"):
    st.session_state.env.add_random_task()
    st.session_state.state = st.session_state.env.get_state()

if st.sidebar.button("🎬 Replay Last Episode"):
    run_replay()

if st.sidebar.button("⚡ Peak Load Test"):
    st.sidebar.warning("Peak Load Mode Activated")
    import random
    num_tasks = random.randint(5, 8)
    for _ in range(num_tasks):
        st.session_state.env.add_random_task()
        # Overwrite last task's deadline for peak load simulation
        st.session_state.env.tasks[-1]["deadline"] = random.randint(5, 15)
    st.session_state.env.logs.append(f"PEAK LOAD: {num_tasks} tasks injected!")
    st.session_state.state = st.session_state.env.get_state()
    st.rerun()

# --- Grid Logic ---
def render_grid(env):
    state = env.get_state()
    grid_size = env.grid_size
    grid = [["▫" for _ in range(grid_size[1])] for _ in range(grid_size[0])]

    for cx, cy in env.charging_stations:
        grid[cx][cy] = "🔋"

    # Visualize planned paths
    for robot in state["robots"]:
        for px, py in robot.get("path", []):
            if grid[px][py] == "▫":
                grid[px][py] = "<span style='color: #38bdf8; opacity: 0.6;'>·</span>"

    for task in state["tasks"]:
        if not task["completed"]:
            px, py = task["pickup"]
            grid[px][py] = f"<div title='Task #{task['id']} Pickup' style='font-size: 24px;'>📦</div>"
            dx, dy = task["drop"]
            grid[dx][dy] = f"<div title='Task #{task['id']} Dropoff' style='font-size: 24px;'>🏁</div>"

    for ox, oy in state.get("obstacles", []):
        grid[ox][oy] = "⬛"

    for cx, cy in state.get("congestion_zones", []):
        grid[cx][cy] = "🟠"

    for robot in state["robots"]:
        rx, ry = robot["position"]
        color = "#0ea5e9" if robot["id"] == 0 else "#8b5cf6"
        grid[rx][ry] = f"<div style='background: {color}; border-radius: 50%; padding: 5px; box-shadow: 0 0 15px {color}88;'>🤖{robot['id']+1}</div>"

    html_rows = []
    html_rows.append("<table style='width: 100%; border-collapse: separate; border-spacing: 8px; text-align: center; font-size: 20px;'>")
    for i in range(grid_size[0]):
        html_rows.append("<tr>")
        for j in range(grid_size[1]):
            cell_val = grid[i][j]
            bg_color = "rgba(30, 41, 59, 0.4)"
            html_rows.append(f"<td class='grid-cell' style='background: {bg_color}; border: 1px solid rgba(56, 189, 248, 0.2); border-radius: 12px; height: 80px; width: 80px; vertical-align: middle;'>{cell_val}</td>")
        html_rows.append("</tr>")
    html_rows.append("</table>")
    return "".join(html_rows)

# 3. Fix Grid Rendering Inside Locked Column
with grid_section:
    st.header("📍 Tactical Operations Grid")
    st.markdown(render_grid(env), unsafe_allow_html=True)

# 3. Lock Telemetry Rendering
with telemetry_section:
    st.header("🤖 Unit Telemetry")
    t_cols = st.columns(len(st.session_state.state["robots"]))
    for idx, robot in enumerate(st.session_state.state["robots"]):
        with t_cols[idx]:
            st.markdown(f"**Unit {robot['id']+1}**")
            st.progress(robot["battery"]/100)
            st.write(f"Pos: {robot['position']} | {'📦 Loaded' if robot['carrying'] else 'Empty'}")

# 4. Lock Task Table
with task_section:
    st.header("📋 Fulfillment Matrix")
    task_list = []
    for task in st.session_state.state["tasks"]:
        p_map = {"HIGH": "🔴 CRITICAL", "NORMAL": "🟡 STANDARD", "LOW": "🟢 LOW"}
        priority_display = p_map.get(task["priority"], task["priority"])
        
        deadline = task["deadline"]
        if task["completed"]: d_display = "✅ FULFILLED"
        elif task.get("failed", False): d_display = "❌ EXPIRED"
        elif deadline <= 5: d_display = f"🔥 URGENT ({deadline})"
        else: d_display = f"🕒 STABLE ({deadline})"

        task_list.append({
            "Unit": f"T-{task['id']}",
            "Priority": priority_display,
            "Timeline": d_display,
            "Route": f"{task['pickup']} → {task['drop']}",
            "Status": "Complete" if task["completed"] else "Active"
        })
    st.dataframe(pd.DataFrame(task_list), use_container_width=True, hide_index=True)

# Lock Event Feed
with event_section:
    st.header("📡 Command Logs")
    for log in reversed(st.session_state.state.get("logs", [])):
        color = "#38bdf8" if "completed" in log.lower() else "#94a3b8"
        if "failed" in log.lower() or "hit" in log.lower(): color = "#f43f5e"
        st.markdown(f"<p style='color: {color}; font-family: monospace; margin: 0;'>[LOG] {log}</p>", unsafe_allow_html=True)

# 2. Move Chart into Persistent Container
with chart_container:
    st.header("📈 Efficiency Matrix")
    if os.path.exists("reward_history.json"):
        with open("reward_history.json", "r") as f:
            try:
                reward_history = json.load(f)
                fig, ax = plt.subplots(figsize=(6, 3))
                fig.patch.set_facecolor('none')
                ax.set_facecolor('none')
                ax.plot(reward_history, color='#38bdf8', linewidth=3, marker='o', markersize=6)
                ax.spines['bottom'].set_color('#94a3b8')
                ax.spines['left'].set_color('#94a3b8')
                ax.tick_params(colors='#94a3b8')
                st.pyplot(fig, clear_figure=True)
            except Exception:
                st.info("Awaiting telemetry stream...")
    
    st.header("🧠 Strategy Allocation")
    usage = st.session_state.state.get("strategy_usage", {})
    if usage:
        df_usage = pd.DataFrame(list(usage.items()), columns=["Strategy", "Usage"])
        st.bar_chart(df_usage.set_index("Strategy"))
        
        # Save to history for learning visualization
        history_file = "strategy_usage_history.json"
        with open(history_file, "w") as f:
            json.dump(usage, f)

    # 📊 Episode Performance Summary Panel
    st.header("📊 Episode Performance Summary")
    summary_file = "episode_summary.json"
    if os.path.exists(summary_file):
        with open(summary_file, "r") as f:
            summary_data = json.load(f)
        
        # Display as a clean grid of metrics
        s_col1, s_col2 = st.columns(2)
        for i, (k, v) in enumerate(summary_data.items()):
            if i % 2 == 0: s_col1.markdown(f"**{k}:** `{v}`")
            else: s_col2.markdown(f"**{k}:** `{v}`")
    else:
        st.info("Complete an episode to view summary.")

if completed_tasks == total_tasks:
    st.balloons()

# --- Elite Documentation ---
with st.expander("🔬 Intelligence Protocol Overview"):
    st.markdown("""
    ### **1. Shortest Path Protocol (BFS)**
    Agents utilize a Breadth-First Search algorithm to calculate the mathematically optimal route. 
    Paths are dynamically recalculated if unit vectors are obstructed by static obstacles (⬛) or dynamic congestion (🟠).
    
    ### **2. Priority-Weighted Scheduling**
    The command engine prioritizes **CRITICAL** tasks using a weighted heuristic that balances deadline urgency with unit energy constraints.
    
    ### **3. Performance Scorecard**
    The system aims for a **90%+ System Rating** by optimizing the `Completed Tasks / Step Count` ratio. 
    Elite ratings are achieved through zero-collision movement and minimized idling.
    """)
