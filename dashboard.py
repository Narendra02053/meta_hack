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
    
    .status-card {
        background: rgba(30, 41, 59, 0.5);
        padding: 1rem;
        border-radius: 0.75rem;
        border-left: 4px solid #38bdf8;
        margin-bottom: 1rem;
    }
    
    .log-entry {
        font-family: 'Courier New', monospace;
        font-size: 0.8rem;
        padding: 0.25rem 0.5rem;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        color: #94a3b8;
    }
</style>
""", unsafe_allow_html=True)

# 1. Implement Persistent Simulation State
if "env" not in st.session_state:
    st.session_state.env = WarehouseEnv()

if "run_steps" not in st.session_state:
    st.session_state.run_steps = 0

if "grid_placeholder" not in st.session_state:
    st.session_state.grid_placeholder = st.empty()

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

m1.metric("Tasks Fulfilled", f"{completed_tasks} / {total_tasks}", delta=f"+{completed_tasks}" if completed_tasks > 0 else None)
m2.metric("Fleet Energy", f"{avg_battery:.1f}%", delta="-1.2%" if st.session_state.run_steps > 0 else None)
m3.metric("Deployment", "HuggingFace", delta="Active", delta_color="normal")

# --- UI Layout Preparation ---
st.sidebar.header("🕹️ Control Center")

# Reset Logic
if st.sidebar.button("🔄 System Reset"):
    st.session_state.env = WarehouseEnv()
    st.session_state.run_steps = 0
    st.session_state.state = st.session_state.env.get_state()
    st.rerun()

# Single Step
if st.sidebar.button("▶️ Execute Step"):
    for robot_id in range(len(env.robots)):
        action = env.intelligent_action(robot_id)
        state, reward, done = env.step(robot_id, action)
    st.session_state.state = state

# Multi-Step Animation
if st.sidebar.button("⏩ Start Full Simulation"):
    st.session_state.run_steps = 25

if st.session_state.run_steps > 0:
    for robot_id in range(len(env.robots)):
        action = env.intelligent_action(robot_id)
        state, reward, done = env.step(robot_id, action)
        if done:
            st.session_state.run_steps = 0
            break

    st.session_state.state = state
    st.session_state.run_steps -= 1
    
    time.sleep(0.12)
    st.rerun()

# --- Grid Logic ---
def render_grid_dataframe(env):
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

    return pd.DataFrame(grid)

# --- Main Layout ---
col_main, col_side = st.columns([2, 1])

with col_main:
    st.header("📍 Real-Time Logistics Grid")
    st.session_state.grid_placeholder.dataframe(
        render_grid_dataframe(env),
        use_container_width=True
    )

    col_a, col_b = st.columns(2)
    with col_a:
        st.header("🤖 Fleet Telemetry")
        if "status_container" not in st.session_state:
            st.session_state.status_container = st.empty()
            
        status_html = []
        for robot in st.session_state.state["robots"]:
            battery_color = "#10b981" if robot["battery"] > 50 else "#f59e0b" if robot["battery"] > 20 else "#ef4444"
            status_html.append(f"""
            <div class="status-card">
                <div style="display: flex; justify-content: space-between;">
                    <b>Agent {robot['id']+1}</b>
                    <span style="color: {battery_color}">{robot['battery']}%</span>
                </div>
                <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 0.25rem;">
                    Loc: {robot['position']} | Carrying: {"Yes 📦" if robot['carrying'] else "Empty"}
                </div>
            </div>
            """)
        st.session_state.status_container.markdown("".join(status_html), unsafe_allow_html=True)

    with col_b:
        st.header("📋 Fulfillment Queue")
        if "task_container" not in st.session_state:
            st.session_state.task_container = st.empty()
            
        task_list = []
        for task in st.session_state.state["tasks"]:
            task_list.append({
                "Ref": f"T#{task['id']}",
                "Pickup": str(task["pickup"]),
                "Drop": str(task["drop"]),
                "State": "Fulfilled" if task["completed"] else "Active"
            })
        st.session_state.task_container.dataframe(pd.DataFrame(task_list), use_container_width=True, hide_index=True)

with col_side:
    st.header("📡 Live Event Feed")
    log_container = st.container(border=True)
    with log_container:
        for log in reversed(st.session_state.state.get("logs", [])):
            st.markdown(f'<div class="log-entry">> {log}</div>', unsafe_allow_html=True)
    
    st.header("📈 Efficiency History")
    if "graph_container" not in st.session_state:
        st.session_state.graph_container = st.empty()

    if os.path.exists("reward_history.json"):
        with open("reward_history.json", "r") as f:
            try:
                reward_history = json.load(f)
                fig, ax = plt.subplots(figsize=(10, 8))
                fig.patch.set_facecolor('none')
                ax.set_facecolor('none')
                
                ax.plot(reward_history, color='#38bdf8', linewidth=2, marker='o', markersize=4)
                ax.fill_between(range(len(reward_history)), reward_history, color='#38bdf8', alpha=0.1)
                
                ax.set_title("Reward Curve", color='#f8fafc')
                ax.tick_params(colors='#94a3b8')
                for spine in ax.spines.values():
                    spine.set_edgecolor('#334155')
                
                st.session_state.graph_container.pyplot(fig)
            except Exception:
                st.info("Loading telemetry...")
    else:
        st.info("No historical data found.")

if completed_tasks == total_tasks:
    st.balloons()
    st.success("Mission Accomplished: All tasks fulfilled with maximum efficiency!")
