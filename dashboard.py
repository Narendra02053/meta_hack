import streamlit as st
import time
import json
import matplotlib.pyplot as plt
import os
import pandas as pd

from warehouse_env import WarehouseEnv

# Page configuration
st.set_page_config(
    page_title="Warehouse AI | Advanced Multi-Agent Logistics",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Aesthetics
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc;
    }
    
    .main .block-container {
        padding-top: 2rem;
    }
    
    h1, h2, h3 {
        color: #38bdf8 !important;
        font-weight: 800 !important;
        letter-spacing: -0.025em;
    }
    
    .stMetric {
        background: rgba(30, 41, 59, 0.7);
        padding: 1.5rem;
        border-radius: 1rem;
        border: 1px solid rgba(56, 189, 248, 0.2);
    }
    
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #0ea5e9 0%, #2563eb 100%);
        color: white;
        border: none;
        padding: 0.6rem 1rem;
        border-radius: 0.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# 1. Implement Persistent Simulation State
if "env" not in st.session_state:
    st.session_state.env = WarehouseEnv()

env = st.session_state.env

if "state" not in st.session_state:
    st.session_state.state = env.get_state()

# Header Section
st.title("🏭 Advanced Warehouse Multi-Agent System")
st.markdown("---")

# Metrics Section
m1, m2, m3 = st.columns(3)
total_tasks = len(st.session_state.state["tasks"])
completed_tasks = sum(1 for t in st.session_state.state["tasks"] if t["completed"])
avg_battery = sum(r["battery"] for r in st.session_state.state["robots"]) / len(st.session_state.state["robots"])

if "total_reward" not in st.session_state:
    st.session_state.total_reward = 0

m1.metric("Tasks Fulfilled", f"{completed_tasks} / {total_tasks}")
m2.metric("Fleet Energy", f"{avg_battery:.1f}%")
m3.metric("System Reward", f"{st.session_state.total_reward}")

# 1. Create Fixed Layout Containers at Top
col_main_layout, col_side_layout = st.columns([2, 1])

with col_main_layout:
    grid_section = st.container()
    col_a, col_b = st.columns(2)
    with col_a:
        telemetry_section = st.container()
    with col_b:
        task_section = st.container()

with col_side_layout:
    event_section = st.container()
    chart_section = st.container()

# --- UI Layout Preparation ---
st.sidebar.header("🕹️ Control Center")

# Reset Logic
if st.sidebar.button("🔄 System Reset"):
    st.session_state.env = WarehouseEnv()
    st.session_state.state = st.session_state.env.get_state()
    st.session_state.total_reward = 0

# Single Step
if st.sidebar.button("Run Step"):
    for robot_id in range(len(env.robots)):
        action = env.intelligent_action(robot_id)
        state, reward, done = env.step(robot_id, action)
        st.session_state.total_reward += reward
    st.session_state.state = env.get_state()

# Multiple Steps
if st.sidebar.button("Run Multiple Steps (10)"):
    for _ in range(10):
        for robot_id in range(len(env.robots)):
            action = env.intelligent_action(robot_id)
            state, reward, done = env.step(robot_id, action)
            st.session_state.total_reward += reward
        time.sleep(0.15)
    st.session_state.state = env.get_state()

# --- Grid Logic ---
def render_grid(env):
    state = env.get_state()
    grid_size = env.grid_size
    grid = [["·" for _ in range(grid_size[1])] for _ in range(grid_size[0])]

    for cx, cy in env.charging_stations:
        grid[cx][cy] = "🔋"

    for task in state["tasks"]:
        if not task["completed"]:
            px, py = task["pickup"]
            grid[px][py] = f"📦{task['id']}"
            dx, dy = task["drop"]
            grid[dx][dy] = f"🏁{task['id']}"

    for robot in state["robots"]:
        rx, ry = robot["position"]
        grid[rx][ry] = f"🤖{robot['id']+1}"

    html_rows = []
    html_rows.append("<table style='width: 100%; border-collapse: collapse; text-align: center; border: 1px solid #ccc; font-size: 20px;'>")
    for i in range(grid_size[0]):
        html_rows.append("<tr>")
        for j in range(grid_size[1]):
            cell_val = grid[i][j].strip()
            html_rows.append(f"<td style='border: 1px solid #ccc; padding: 15px;'>{cell_val}</td>")
        html_rows.append("</tr>")
    html_rows.append("</table>")
    return "".join(html_rows)

# 2. Render Grid Inside Locked Container
with grid_section:
    st.header("📍 Real-Time Logistics Grid")
    st.markdown(render_grid(env), unsafe_allow_html=True)

# 3. Lock Telemetry Rendering
with telemetry_section:
    st.header("🤖 Fleet Telemetry")
    for robot in st.session_state.state["robots"]:
        st.write(
            f"Robot {robot['id']} → {robot['position']} | "
            f"Battery: {robot['battery']} | "
            f"Carrying: {robot['carrying']}"
        )

# 4. Lock Task Table
with task_section:
    st.header("📋 Fulfillment Queue")
    task_list = []
    for task in st.session_state.state["tasks"]:
        task_list.append({
            "Ref": f"T#{task['id']}",
            "Pickup": str(task["pickup"]),
            "Drop": str(task["drop"]),
            "State": "Fulfilled" if task["completed"] else "Active"
        })
    st.dataframe(pd.DataFrame(task_list), use_container_width=True, hide_index=True)

# Lock Event Feed
with event_section:
    st.header("📡 Live Event Feed")
    for log in reversed(st.session_state.state.get("logs", [])):
        st.write(f"> {log}")

# 5. Lock Chart Rendering
with chart_section:
    st.header("📈 Efficiency History")
    if os.path.exists("reward_history.json"):
        with open("reward_history.json", "r") as f:
            try:
                reward_history = json.load(f)
                fig, ax = plt.subplots(figsize=(10, 8))
                ax.plot(reward_history, color='#38bdf8', linewidth=2, marker='o', markersize=4)
                st.pyplot(fig, clear_figure=True)
            except Exception:
                st.info("Loading telemetry...")

if completed_tasks == total_tasks:
    st.success("Mission Accomplished: All tasks fulfilled!")
