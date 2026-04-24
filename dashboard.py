import streamlit as st
import time
import pandas as pd
import json
import matplotlib.pyplot as plt
import os

from warehouse_env import WarehouseEnv

# Page configuration
st.set_page_config(page_title="Warehouse AI Dashboard", layout="wide")

# 1. Persist Environment Properly
if "env" not in st.session_state:
    st.session_state.env = WarehouseEnv()

env = st.session_state.env

if "state" not in st.session_state:
    st.session_state.state = env.get_state()

st.title("🏭 Multi-Agent Warehouse Environment")

# --- Function to Render Grid ---
def render_grid(state):
    grid_size = env.grid_size
    grid = [["" for _ in range(grid_size[1])] for _ in range(grid_size[0])]

    # Highlight Charging Stations
    for cx, cy in env.charging_stations:
        grid[cx][cy] += "C "

    # Mark Tasks (P and D)
    for task in state["tasks"]:
        if not task["completed"]:
            px, py = task["pickup"]
            grid[px][py] += f"P{task['id']} "
            dx, dy = task["drop"]
            grid[dx][dy] += f"D{task['id']} "

    # Mark Robots
    for robot in state["robots"]:
        rx, ry = robot["position"]
        grid[rx][ry] += f"R{robot['id']+1} "

    # Clean up empty cells
    for i in range(grid_size[0]):
        for j in range(grid_size[1]):
            if grid[i][j] == "":
                grid[i][j] = "-"
            else:
                grid[i][j] = grid[i][j].strip()

    return pd.DataFrame(grid)

# --- Layout ---
st.sidebar.header("Controls")

st.header("1. Warehouse Grid")
# 7. Optimize Grid Rendering using st.empty container
grid_placeholder = st.empty()
grid_placeholder.dataframe(render_grid(st.session_state.state), use_container_width=True)

if st.sidebar.button("Run Step"):
    # 5. Stabilize Position Rendering: position changes only once per step
    for robot_id in range(len(env.robots)):
        action = env.intelligent_action(robot_id)
        st.session_state.state, reward, done = env.step(robot_id, action)
    st.rerun()

if st.sidebar.button("Run Multiple Steps (10)"):
    # 3. Fix Multiple Steps Execution (Update state inside loop but redraw UI once)
    for _ in range(10):
        for robot_id in range(len(env.robots)):
            action = env.intelligent_action(robot_id)
            st.session_state.state, reward, done = env.step(robot_id, action)
        
        # 4. Add Frame Control Delay
        time.sleep(0.05)
    
    # Redraw grid only once after loop ends
    st.rerun()

if st.sidebar.button("Reset Environment"):
    # 6. Avoid Full Page Reset (no st.session_state.clear())
    env.reset()
    st.session_state.state = env.get_state()
    st.rerun()

# Layout for Status
col1, col2 = st.columns(2)

with col1:
    st.header("2. Robot Status")
    status_content = ""
    for robot in st.session_state.state["robots"]:
        status_content += f"**Robot {robot['id']}** → {robot['position']} | Battery: {robot['battery']} | Carrying: {robot['carrying']}\n\n"
    st.info(status_content)

with col2:
    st.header("3. Task Status")
    task_data = []
    for task in st.session_state.state["tasks"]:
        task_data.append({
            "Task ID": task["id"],
            "Pickup Location": str(task["pickup"]),
            "Drop Location": str(task["drop"]),
            "Completed Status": "✅" if task["completed"] else "❌"
        })
    st.table(pd.DataFrame(task_data))

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
