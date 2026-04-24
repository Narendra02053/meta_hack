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

# 4. Prevent Layout Jumping
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    section.main > div {
        padding-top: 1rem;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc;
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

if "total_reward" not in st.session_state:
    st.session_state.total_reward = 0

# Header Section
st.title("🏭 Advanced Warehouse Multi-Agent System")
st.markdown("---")

# Metrics Section
m1, m2, m3 = st.columns(3)
total_tasks = len(st.session_state.state["tasks"])
completed_tasks = sum(1 for t in st.session_state.state["tasks"] if t["completed"])
avg_battery = sum(r["battery"] for r in st.session_state.state["robots"]) / len(st.session_state.state["robots"])

m1.metric("Tasks Fulfilled", f"{completed_tasks} / {total_tasks}")
m2.metric("Fleet Energy", f"{avg_battery:.1f}%")
m3.metric("System Reward", f"{st.session_state.total_reward}")

# 1. Create Fixed Layout Columns Once
col_grid, col_chart = st.columns([2, 1])

# Persistent Containers
grid_section = col_grid.container()
telemetry_section = col_grid.container()
task_section = col_grid.container()
chart_container = col_chart.container()
event_section = col_chart.container()

# --- UI Layout Preparation ---
st.sidebar.header("🕹️ Control Center")

# Reset Logic
if st.sidebar.button("🔄 System Reset"):
    # Save performance before reset
    if st.session_state.env.step_count > 0:
        history_file = "reward_history.json"
        history = []
        if os.path.exists(history_file):
            with open(history_file, "r") as f:
                try:
                    history = json.load(f)
                except:
                    history = []
        
        history.append(st.session_state.total_reward)
        with open(history_file, "w") as f:
            json.dump(history, f)
            
    st.session_state.env = WarehouseEnv()
    st.session_state.state = st.session_state.env.get_state()
    st.session_state.total_reward = 0
    st.rerun()

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

# Dynamic Task Injection
if st.sidebar.button("📦 Inject Emergency Task"):
    st.session_state.env.add_random_task()
    st.session_state.state = st.session_state.env.get_state()

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
                grid[px][py] = "·"

    for task in state["tasks"]:
        if not task["completed"]:
            px, py = task["pickup"]
            grid[px][py] = f"📦{task['id']}"
            dx, dy = task["drop"]
            grid[dx][dy] = f"🏁{task['id']}"

    for ox, oy in state.get("obstacles", []):
        grid[ox][oy] = "⬛"

    for cx, cy in state.get("congestion_zones", []):
        grid[cx][cy] = "🟠"

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

# 3. Fix Grid Rendering Inside Locked Column
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
        priority_display = {
            "HIGH": "🔴 HIGH",
            "NORMAL": "🟡 NORMAL",
            "LOW": "🟢 LOW"
        }.get(task["priority"], task["priority"])
        
        # Deadline visualization
        deadline = task["deadline"]
        if task["completed"]:
            deadline_display = "✅ Done"
        elif task.get("failed", False):
            deadline_display = "❌ Expired"
        elif deadline <= 5:
            deadline_display = f"🔴 Critical ({deadline})"
        elif deadline <= 10:
            deadline_display = f"🟡 Warning ({deadline})"
        else:
            deadline_display = f"🟢 Safe ({deadline})"

        task_list.append({
            "Ref": f"T#{task['id']}",
            "Priority": priority_display,
            "Deadline": deadline_display,
            "Pickup": str(task["pickup"]),
            "Drop": str(task["drop"]),
            "State": "Fulfilled" if task["completed"] else "Failed" if task.get("failed") else "Active"
        })
    st.dataframe(pd.DataFrame(task_list), use_container_width=True, hide_index=True)

    # STEP 5 — Add Episode Summary Panel to Dashboard
    st.header("📊 Episode Summary")
    completed_tasks = sum(1 for t in env.tasks if t["completed"])
    total_tasks = len(env.tasks)
    
    col_e1, col_e2, col_e3 = st.columns(3)
    col_e1.metric("Tasks Completed", f"{completed_tasks}/{total_tasks}")
    col_e2.metric("Total Steps", env.step_count)
    col_e3.metric("Total Reward", env.total_reward)

    # STEP 7 — Optional Efficiency Score
    if env.step_count > 0:
        efficiency = completed_tasks / env.step_count
        st.metric("Efficiency Score", round(efficiency, 2))

    # STEP 6 — Add Success Message
    if completed_tasks == total_tasks:
        st.success("🎉 All Tasks Completed Successfully!")

# Lock Event Feed
with event_section:
    st.header("📡 Live Event Feed")
    for log in reversed(st.session_state.state.get("logs", [])):
        st.write(f"> {log}")

# 2. Move Chart into Persistent Container
with chart_container:
    st.header("📈 Efficiency History")
    if os.path.exists("reward_history.json"):
        with open("reward_history.json", "r") as f:
            try:
                reward_history = json.load(f)
                # 5. Reduce Chart Size
                fig, ax = plt.subplots(figsize=(6, 3))
                ax.plot(reward_history, color='#38bdf8', linewidth=2, marker='o', markersize=4)
                ax.set_title("Reward vs Episode")
                st.pyplot(fig, clear_figure=True)
            except Exception:
                st.info("Loading telemetry...")

if completed_tasks == total_tasks:
    # We already showed the success message inside the container, but the balloons are nice
    st.balloons()

# --- Judge-Ready Documentation ---
with st.expander("🔬 System Architecture & Intelligence Overview"):
    st.markdown("""
    ### **1. Multi-Agent Coordination**
    The system utilizes a **Decentralized Intelligence** model where each agent (🤖) independently evaluates the warehouse state to determine its optimal action. 
    
    ### **2. Pathfinding & Collision Avoidance**
    Agents implement a priority-based movement strategy:
    - **Battery Management**: If battery levels drop below **20%**, agents override task assignments to navigate to the nearest charging station (🔋).
    - **Dynamic Rerouting**: Agents scan for obstacles (other robots) in their preferred direction. If blocked, they will wait or attempt a secondary route to prevent gridlock.
    - **Action Logic**: Agents automatically transition between *Navigation*, *Pickup* (📦), and *Drop-off* (🏁) states based on task assignment.

    ### **3. Reward & Performance Metrics**
    The environment provides granular feedback to evaluate agent efficiency:
    - **Step Penalty (-1)**: Encourages the shortest possible paths.
    - **Wall/Collision Penalty (-5 to -20)**: Enforces safety constraints.
    - **Task Fulfillment (+50 to +100)**: Primary objective success.
    - **Efficiency Score**: Calculated as `Completed Tasks / Total Steps`. High values indicate optimized multi-agent coordination.
    """)
