import streamlit as st
import time
import json
import matplotlib.pyplot as plt
import os
import pandas as pd

from warehouse_priority_env.grid_env import GridWarehouseEnv as WarehouseEnv

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
    .stPlot canvas {
        height: 400px !important;
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

def render_grid(env_obj):
    state = env_obj.get_state()
    grid_size = env_obj.grid_size
    grid = [["▫" for _ in range(grid_size[1])] for _ in range(grid_size[0])]

    for cx, cy in env_obj.charging_stations:
        grid[cx][cy] = "🔋"

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

    html_rows = ["<table style='width: 100%; border-collapse: separate; border-spacing: 8px; text-align: center; font-size: 20px;'>"]
    for i in range(grid_size[0]):
        html_rows.append("<tr>")
        for j in range(grid_size[1]):
            cell_val = grid[i][j]
            bg_color = "rgba(30, 41, 59, 0.4)"
            html_rows.append(f"<td class='grid-cell' style='background: {bg_color}; border: 1px solid rgba(56, 189, 248, 0.2); border-radius: 12px; height: 80px; width: 80px; vertical-align: middle;'>{cell_val}</td>")
        html_rows.append("</tr>")
    html_rows.append("</table>")
    return "".join(html_rows)

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
        
        class MockEnv:
            def __init__(self, state_data):
                self.state = state_data
                self.grid_size = (5, 5)
                self.charging_stations = [(0, 0), (4, 4)]
                self.obstacles = state_data.get("obstacles", [])
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

def update_charts():
    if os.path.exists("reward_history.json"):
        with open("reward_history.json", "r") as f:
            try:
                reward_history = json.load(f)
                fig, ax = plt.subplots()
                fig.set_size_inches(8, 4)
                fig.patch.set_facecolor('none')
                ax.set_facecolor('none')
                ax.plot(reward_history, color='#38bdf8', linewidth=3, marker='o', markersize=6)
                ax.spines['bottom'].set_color('#94a3b8')
                ax.spines['left'].set_color('#94a3b8')
                ax.tick_params(colors='#94a3b8')
                eff_chart_placeholder.pyplot(fig, width='content')
                plt.close(fig)
            except: pass

    usage = st.session_state.state.get("strategy_usage", {})
    if usage:
        df_usage = pd.DataFrame(list(usage.items()), columns=["Strategy", "Usage"])
        fig2, ax2 = plt.subplots()
        fig2.set_size_inches(6, 4)
        fig2.patch.set_facecolor('none')
        ax2.set_facecolor('none')
        ax2.bar(df_usage["Strategy"], df_usage["Usage"], color='#38bdf8')
        ax2.spines['bottom'].set_color('#94a3b8')
        ax2.spines['left'].set_color('#94a3b8')
        ax2.tick_params(colors='#94a3b8', labelsize=8)
        strategy_chart_placeholder.pyplot(fig2, width='content')
        plt.close(fig2)
        
        history_file = "strategy_usage_history.json"
        with open(history_file, "w") as f:
            json.dump(usage, f)

# Metrics Section
completed_tasks = sum(1 for t in st.session_state.state["tasks"] if t["completed"])
total_tasks = len(st.session_state.state["tasks"])
avg_battery = sum(r["battery"] for r in st.session_state.state["robots"]) / len(st.session_state.state["robots"])

# Performance Rating Logic
perf_rating = 0
if env.step_count > 0:
    success_rate = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
    efficiency = min(1.0, (completed_tasks / env.step_count) * 5)
    perf_rating = int((success_rate * 0.7) + (efficiency * 30))

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Task Success", f"{completed_tasks}/{total_tasks}", delta=f"{int((completed_tasks/total_tasks)*100)}%" if total_tasks > 0 else "0%")
m2.metric("Fleet Status", f"{avg_battery:.0f}%", delta="Charging" if avg_battery < 30 else "Optimal", delta_color="normal")
m3.metric("System Rating", f"{perf_rating}%", delta="Elite" if perf_rating >= 90 else "Analyzing")
m4.metric("🤝 Coordination", f"{st.session_state.state.get('coordination_score', 0)}")
m5.metric("Total Reward", f"{st.session_state.total_reward}")

# Columns
col_grid, col_chart = st.columns([1.8, 1.2])

# Placeholders for stable chart rendering
with col_chart:
    st.header("📈 Efficiency Matrix")
    eff_container = st.container(height=420)
    eff_chart_placeholder = eff_container.empty()
    
    st.header("🧠 Strategy Allocation")
    strategy_container = st.container(height=420)
    strategy_chart_placeholder = strategy_container.empty()

# Sidebar Controls
st.sidebar.header("🕹️ Mission Control")

if st.sidebar.button("🔄 Full System Reset"):
    if st.session_state.env.step_count > 0:
        save_episode_data()
        history_file = "reward_history.json"
        history = []
        if os.path.exists(history_file):
            with open(history_file, "r") as f:
                try: history = json.load(f)
                except: history = []
        history.append(st.session_state.total_reward)
        with open(history_file, "w") as f:
            json.dump(history, f)
            
    st.session_state.env = WarehouseEnv()
    st.session_state.state = st.session_state.env.get_state()
    st.session_state.total_reward = 0
    st.rerun()

st.sidebar.markdown("---")

if st.sidebar.button("▶️ Execute Next Phase"):
    for robot_id in range(len(env.robots)):
        action = env.intelligent_action(robot_id)
        state, reward, done = env.step(robot_id, action)
        st.session_state.total_reward += reward
        if done:
            save_episode_data()
            break
    st.session_state.state = env.get_state()
    update_charts()

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
            st.session_state.state = env.get_state()
            update_charts()
            break
        st.session_state.state = env.get_state()
        update_charts()
        time.sleep(0.1)

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
        st.session_state.env.tasks[-1]["deadline"] = random.randint(5, 15)
    st.session_state.env.logs.append(f"PEAK LOAD: {num_tasks} tasks injected!")
    st.session_state.state = st.session_state.env.get_state()
    st.rerun()

# Main Grid
with col_grid:
    st.header("📍 Tactical Operations Grid")
    st.markdown(render_grid(env), unsafe_allow_html=True)
    
    st.markdown("---")
    t_c1, t_c2 = st.columns([2, 1])
    with t_c1:
        st.header("🤖 Unit Telemetry")
        t_cols = st.columns(len(st.session_state.state["robots"]))
        for idx, robot in enumerate(st.session_state.state["robots"]):
            with t_cols[idx]:
                st.markdown(f"**Unit {robot['id']+1}**")
                st.progress(robot["battery"]/100)
                st.write(f"Pos: {robot['position']} | {'📦 Loaded' if robot['carrying'] else 'Empty'}")
    
    with t_c2:
        st.header("🧠 Strategy Monitor")
        s_data = st.session_state.state
        st.markdown(f"**Current:** `{s_data.get('current_strategy', 'None')}`")
        st.markdown(f"**Reason:** *{s_data.get('strategy_reason', 'N/A')}*")
        st.write(f"Tasks: {s_data.get('pending_tasks', 0)} | Min DL: {s_data.get('min_deadline', 0)}")

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

# Main Grid Rendering


update_charts()

with col_chart:
    st.header("📊 Episode Performance Summary")
    if os.path.exists("episode_summary.json"):
        with open("episode_summary.json", "r") as f:
            summary_data = json.load(f)
        s_col1, s_col2 = st.columns(2)
        for i, (k, v) in enumerate(summary_data.items()):
            if i % 2 == 0: s_col1.markdown(f"**{k}:** `{v}`")
            else: s_col2.markdown(f"**{k}:** `{v}`")
    else: st.info("Finish an episode for summary.")

    st.header("📡 Command Logs")
    for log in reversed(st.session_state.state.get("logs", [])):
        color = "#38bdf8" if "completed" in log.lower() else "#94a3b8"
        if "failed" in log.lower() or "hit" in log.lower(): color = "#f43f5e"
        st.markdown(f"<p style='color: {color}; font-family: monospace; margin: 0;'>[LOG] {log}</p>", unsafe_allow_html=True)

if completed_tasks == total_tasks:
    st.balloons()
