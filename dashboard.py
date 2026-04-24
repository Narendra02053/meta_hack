import streamlit as st
import time
import json
import matplotlib.pyplot as plt
import os

from warehouse_env import WarehouseEnv

# Page configuration
st.set_page_config(page_title="Warehouse AI Dashboard", layout="wide")

# 1. Add Simulation Control Variables
if "env" not in st.session_state:
    st.session_state.env = WarehouseEnv()

if "run_steps" not in st.session_state:
    st.session_state.run_steps = 0

if "grid_placeholder" not in st.session_state:
    st.session_state.grid_placeholder = st.empty()

env = st.session_state.env

if "state" not in st.session_state:
    st.session_state.state = env.get_state()

st.title("🏭 Multi-Agent Warehouse Environment")

# --- UI Layout Preparation ---
st.sidebar.header("Controls")

# 7. Implement Safe Reset Logic
if st.sidebar.button("Reset Environment"):
    st.session_state.env = WarehouseEnv()
    st.session_state.run_steps = 0
    st.session_state.state = st.session_state.env.get_state()
    st.rerun()

# 3. Fix Single Step Execution
if st.sidebar.button("Run Step"):
    for robot_id in range(len(env.robots)):
        action = env.intelligent_action(robot_id)
        env.step(robot_id, action)
    st.session_state.state = env.get_state()

# 2. Convert Multi-Step Execution into Frame Execution
if st.sidebar.button("Run Multiple Steps (10)"):
    st.session_state.run_steps = 10

if st.session_state.run_steps > 0:
    for robot_id in range(len(env.robots)):
        action = env.intelligent_action(robot_id)
        env.step(robot_id, action)

    st.session_state.state = env.get_state()
    st.session_state.run_steps -= 1
    
    # 8. Add Frame Delay
    time.sleep(0.12)
    st.rerun()


# --- 7. Optimize HTML Rendering ---
def render_grid(env):
    state = env.get_state()
    grid_size = env.grid_size
    grid = [["" for _ in range(grid_size[1])] for _ in range(grid_size[0])]

    for cx, cy in env.charging_stations:
        grid[cx][cy] += "C "

    for task in state["tasks"]:
        if not task["completed"]:
            px, py = task["pickup"]
            grid[px][py] += f"P{task['id']} "
            dx, dy = task["drop"]
            grid[dx][dy] += f"D{task['id']} "

    for robot in state["robots"]:
        rx, ry = robot["position"]
        grid[rx][ry] += f"R{robot['id']+1} "

    html_rows = []
    html_rows.append("<table style='width: 100%; border-collapse: collapse; text-align: center; border: 1px solid #ccc; font-size: 20px;'>")
    for i in range(grid_size[0]):
        html_rows.append("<tr>")
        for j in range(grid_size[1]):
            cell_val = grid[i][j].strip()
            if cell_val == "":
                cell_val = "-"
            html_rows.append(f"<td style='border: 1px solid #ccc; padding: 20px; font-weight: bold;'>{cell_val}</td>")
        html_rows.append("</tr>")
    html_rows.append("</table>")
    return "".join(html_rows)

# --- 4. Separate Simulation Logic From Rendering Logic ---
st.header("1. Warehouse Grid")

# 4. Use Persistent Grid Placeholder
st.session_state.grid_placeholder.markdown(
    render_grid(env),
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)

with col1:
    st.header("2. Robot Status")
    if "status_container" not in st.session_state:
        st.session_state.status_container = st.empty()
        
    status_content = ""
    for robot in st.session_state.state["robots"]:
        status_content += f"**Robot {robot['id']}** → {robot['position']} | Battery: {robot['battery']} | Carrying: {robot['carrying']}<br><br>"
    st.session_state.status_container.markdown(status_content, unsafe_allow_html=True)

with col2:
    st.header("3. Task Status")
    if "task_container" not in st.session_state:
        st.session_state.task_container = st.empty()
        
    task_html_list = ["<table style='width: 100%; border-collapse: collapse; text-align: center; border: 1px solid #ccc;'><tr><th style='border: 1px solid #ccc; padding: 8px;'>Task ID</th><th style='border: 1px solid #ccc; padding: 8px;'>Pickup Location</th><th style='border: 1px solid #ccc; padding: 8px;'>Drop Location</th><th style='border: 1px solid #ccc; padding: 8px;'>Completed Status</th></tr>"]
    for task in st.session_state.state["tasks"]:
        status = "✅" if task["completed"] else "❌"
        task_html_list.append(f"<tr><td style='border: 1px solid #ccc; padding: 8px;'>{task['id']}</td><td style='border: 1px solid #ccc; padding: 8px;'>{task['pickup']}</td><td style='border: 1px solid #ccc; padding: 8px;'>{task['drop']}</td><td style='border: 1px solid #ccc; padding: 8px;'>{status}</td></tr>")
    task_html_list.append("</table>")
    st.session_state.task_container.markdown("".join(task_html_list), unsafe_allow_html=True)

st.header("5. Reward History Graph")

if "graph_container" not in st.session_state:
    st.session_state.graph_container = st.empty()

if os.path.exists("reward_history.json"):
    with open("reward_history.json", "r") as f:
        try:
            reward_history = json.load(f)
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot(reward_history, marker='o', linestyle='-', markersize=3, color='royalblue')
            ax.set_title("Reward vs Episode", fontsize=14)
            ax.set_xlabel("Episode", fontsize=12)
            ax.set_ylabel("Reward", fontsize=12)
            ax.grid(True, linestyle='--', alpha=0.7)
            st.session_state.graph_container.pyplot(fig)
        except json.JSONDecodeError:
            st.warning("Invalid reward history data.")
else:
    st.warning("`reward_history.json` not found in the directory.")
