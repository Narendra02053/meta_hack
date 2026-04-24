import streamlit as st
import time
import json
import matplotlib.pyplot as plt
import os

from warehouse_env import WarehouseEnv

st.set_page_config(page_title="Warehouse AI Dashboard", layout="wide")

if "env" not in st.session_state:
    st.session_state.env = WarehouseEnv()

env = st.session_state.env

if "state" not in st.session_state:
    st.session_state.state = env.get_state()

st.title("🏭 Multi-Agent Warehouse Environment")

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

    html = "<table style='width: 100%; border-collapse: collapse; text-align: center; border: 1px solid #ccc; font-size: 20px;'>"
    for i in range(grid_size[0]):
        html += "<tr>"
        for j in range(grid_size[1]):
            cell_val = grid[i][j].strip()
            if cell_val == "":
                cell_val = "-"
            html += f"<td style='border: 1px solid #ccc; padding: 20px; font-weight: bold;'>{cell_val}</td>"
        html += "</tr>"
    html += "</table>"
    return html

st.sidebar.header("Controls")

if st.sidebar.button("Run Step"):

    for robot_id in range(len(env.robots)):
        action = env.intelligent_action(robot_id)
        env.step(robot_id, action)

    st.session_state.state = env.get_state()

if st.sidebar.button("Run Multiple Steps (10)"):

    for _ in range(10):

        for robot_id in range(len(env.robots)):
            action = env.intelligent_action(robot_id)
            env.step(robot_id, action)

        time.sleep(0.12)

    st.session_state.state = env.get_state()

if st.sidebar.button("Reset Environment"):
    env.reset()
    st.session_state.state = env.get_state()
    st.rerun()

st.header("1. Warehouse Grid")
if "grid_container" not in st.session_state:
    st.session_state.grid_container = st.empty()

st.session_state.grid_container.markdown(
    render_grid(env),
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)

with col1:
    st.header("2. Robot Status")
    status_content = ""
    for robot in st.session_state.state["robots"]:
        status_content += f"**Robot {robot['id']}** → {robot['position']} | Battery: {robot['battery']} | Carrying: {robot['carrying']}<br><br>"
    st.markdown(status_content, unsafe_allow_html=True)

with col2:
    st.header("3. Task Status")
    task_html = "<table style='width: 100%; border-collapse: collapse; text-align: center; border: 1px solid #ccc;'><tr><th style='border: 1px solid #ccc; padding: 8px;'>Task ID</th><th style='border: 1px solid #ccc; padding: 8px;'>Pickup Location</th><th style='border: 1px solid #ccc; padding: 8px;'>Drop Location</th><th style='border: 1px solid #ccc; padding: 8px;'>Completed Status</th></tr>"
    for task in st.session_state.state["tasks"]:
        status = "✅" if task["completed"] else "❌"
        task_html += f"<tr><td style='border: 1px solid #ccc; padding: 8px;'>{task['id']}</td><td style='border: 1px solid #ccc; padding: 8px;'>{task['pickup']}</td><td style='border: 1px solid #ccc; padding: 8px;'>{task['drop']}</td><td style='border: 1px solid #ccc; padding: 8px;'>{status}</td></tr>"
    task_html += "</table>"
    st.markdown(task_html, unsafe_allow_html=True)

st.header("5. Reward History Graph")

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
            st.pyplot(fig)
        except json.JSONDecodeError:
            st.warning("Invalid reward history data.")
else:
    st.warning("`reward_history.json` not found in the directory.")
