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
        background: radial-gradient(circle at top right, #0f172a, #000000);
        color: #f8fafc;
    }
    
    [data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        color: #38bdf8 !important;
    }

    .brain-status {
        display: flex;
        align-items: center;
        background: rgba(15, 23, 42, 0.8);
        padding: 0.5rem 1rem;
        border-radius: 2rem;
        border: 1px solid #38bdf8;
        margin-bottom: 2rem;
    }

    .pulse {
        width: 12px;
        height: 12px;
        background: #10b981;
        border-radius: 50%;
        margin-right: 10px;
        box-shadow: 0 0 0 rgba(16, 185, 129, 0.4);
        animation: pulse-animation 2s infinite;
    }

    @keyframes pulse-animation {
        0% { box-shadow: 0 0 0 0px rgba(16, 185, 129, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
        100% { box-shadow: 0 0 0 0px rgba(16, 185, 129, 0); }
    }
    
    canvas {
        border-radius: 1rem;
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
if "pos_reward" not in st.session_state: st.session_state.pos_reward = 0
if "neg_reward" not in st.session_state: st.session_state.neg_reward = 0
if "reward_trace" not in st.session_state: st.session_state.reward_trace = []
if "last_reward" not in st.session_state: st.session_state.last_reward = None
if "reward_log" not in st.session_state: st.session_state.reward_log = []

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
st.markdown("""
<div class='brain-status'>
    <div class='pulse'></div>
    <div style='color: #38bdf8; font-weight: 600; font-size: 0.9rem;'>
        PYTORCH NEURAL POLICY ENGINE: <span style='color: #10b981;'>ACTIVE</span>
    </div>
</div>
""", unsafe_allow_html=True)
st.markdown("<p style='color: #94a3b8; font-size: 1.1rem; margin-top: -1rem;'>Autonomous Logistics Optimization Engine v2.5 [PyTorch-DQN]</p>", unsafe_allow_html=True)

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
throughput = 0
avg_completion = st.session_state.state.get("avg_completion_time", 0)

if env.step_count > 0:
    success_rate = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
    efficiency = min(1.0, (completed_tasks / env.step_count) * 5)
    perf_rating = int((success_rate * 0.7) + (efficiency * 30))
    throughput = (completed_tasks / env.step_count) * 100

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("📦 Task Success", f"{completed_tasks}/{total_tasks}", delta=f"{int((completed_tasks/total_tasks)*100)}%" if total_tasks > 0 else "0%")
m2.metric("⚡ System Throughput", f"{throughput:.1f}", help="Tasks per 100 operational steps")
m3.metric("🏆 System Rating", f"{perf_rating}%", delta="Elite" if perf_rating >= 90 else "Analyzing")
m4.metric("🤝 Coordination", f"{st.session_state.state.get('coordination_score', 0)}")
m5.metric("⏱️ Avg Cycle Time", f"{avg_completion:.1f}s")

# ── ⚡ Reward Feed ─────────────────────────────────────────────
def _reward_label(r):
    if r >= 150: return "✅ All tasks complete!"
    elif r >= 60: return "✅ Task delivered"
    elif r >= 15: return "✅ Item picked up"
    elif r >= 10: return "✅ Recharged / Priority bonus"
    elif r == -1: return "⚙️ Movement"
    elif r <= -20: return "❌ Collision / Deadline missed"
    elif r <= -10: return "❌ Obstacle hit / Battery dead"
    else: return "⚙️ Step penalty"

with st.container():
    st.markdown("### ⚡ Reward Feed")
    feed_left, feed_right = st.columns([1, 2])
    with feed_left:
        if st.session_state.last_reward is not None:
            lr = st.session_state.last_reward
            color = "#10b981" if lr >= 0 else "#f43f5e"
            sign = "+" if lr >= 0 else ""
            st.markdown(f"""
            <div style='background:rgba(15,23,42,0.7);border:1px solid {color};
                        border-radius:1rem;padding:1rem;text-align:center;'>
                <div style='font-size:0.8rem;color:#94a3b8;'>LAST REWARD</div>
                <div style='font-size:2.5rem;font-weight:800;color:{color};'>{sign}{lr:.0f}</div>
            </div>""", unsafe_allow_html=True)
        else:
            st.info("Run a step to see rewards.")
    with feed_right:
        if st.session_state.reward_log:
            for entry in reversed(st.session_state.reward_log[-10:]):
                r = entry["reward"]
                color = "#10b981" if r >= 0 else "#f43f5e"
                sign = "+" if r >= 0 else ""
                st.markdown(f"""
                <div style='display:flex;justify-content:space-between;
                            background:rgba(15,23,42,0.5);padding:0.3rem 0.8rem;
                            border-radius:0.5rem;margin-bottom:4px;
                            border-left:3px solid {color};'>
                    <span style='color:{color};font-weight:700;font-family:monospace;'>{sign}{r:.0f}</span>
                    <span style='color:#94a3b8;font-size:0.85rem;'>{entry['label']}</span>
                </div>""", unsafe_allow_html=True)
        else:
            st.caption("No reward events yet.")
st.markdown("---")
# ──────────────────────────────────────────────────────────────

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
    st.session_state.pos_reward = 0
    st.session_state.neg_reward = 0
    st.session_state.reward_trace = []
    st.session_state.last_reward = None
    st.session_state.reward_log = []
    st.rerun()

st.sidebar.markdown("---")

if st.sidebar.button("▶️ Execute Next Phase"):
    for robot_id in range(len(env.robots)):
        action = env.intelligent_action(robot_id)
        state, reward, done = env.step(robot_id, action)
        st.session_state.total_reward += reward
        if reward > 0: st.session_state.pos_reward += reward
        elif reward < 0: st.session_state.neg_reward += reward
        st.session_state.reward_trace.append(reward)
        st.session_state.last_reward = reward
        st.session_state.reward_log = (st.session_state.reward_log + [{"reward": reward, "label": _reward_label(reward)}])[-10:]
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
            if reward > 0: st.session_state.pos_reward += reward
            elif reward < 0: st.session_state.neg_reward += reward
            st.session_state.reward_trace.append(reward)
            st.session_state.last_reward = reward
            st.session_state.reward_log = (st.session_state.reward_log + [{"reward": reward, "label": _reward_label(reward)}])[-10:]
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

    # --- REWARD TRACKER SECTION ---
    st.header("🎯 Live Reward Tracker")
    r_c1, r_c2, r_c3 = st.columns(3)
    r_c1.metric("Total", f"{st.session_state.total_reward:.1f}")
    r_c2.metric("Positive", f"{st.session_state.pos_reward:.1f}")
    r_c3.metric("Negative", f"{st.session_state.neg_reward:.1f}")
    
    if st.session_state.reward_trace:
        trace = st.session_state.reward_trace[-50:]
        fig_rew, ax_rew = plt.subplots(figsize=(6, 3))
        colors = ['#10b981' if r > 0 else '#f43f5e' for r in trace]
        ax_rew.bar(range(len(trace)), trace, color=colors)
        ax_rew.set_facecolor('none')
        fig_rew.patch.set_facecolor('none')
        ax_rew.spines['bottom'].set_color('#94a3b8')
        ax_rew.spines['left'].set_color('#94a3b8')
        ax_rew.tick_params(colors='#94a3b8', labelsize=8)
        ax_rew.set_title("Reward per Step (Last 50)", color='#38bdf8', fontsize=10)
        st.pyplot(fig_rew, width='content')
        plt.close(fig_rew)

    st.header("📡 Command Logs")
    for log in reversed(st.session_state.state.get("logs", [])):
        color = "#38bdf8" if "completed" in log.lower() else "#94a3b8"
        if "failed" in log.lower() or "hit" in log.lower(): color = "#f43f5e"
        st.markdown(f"<p style='color: {color}; font-family: monospace; margin: 0;'>[LOG] {log}</p>", unsafe_allow_html=True)

if completed_tasks == total_tasks:
    st.balloons()
