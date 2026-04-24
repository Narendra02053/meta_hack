import streamlit as st
import time
import pandas as pd
import json
import matplotlib.pyplot as plt
import os

from warehouse_env import WarehouseEnv

# Page configuration
st.set_page_config(page_title="Warehouse AI Dashboard", layout="wide")

# Initialize the environment in session state
if "env" not in st.session_state:
    st.session_state.env = WarehouseEnv()

# Use the env variable properly
env = st.session_state.env

if "state" not in st.session_state:
    st.session_state.state = env.get_state()

st.title("🏭 Multi-Agent Warehouse Environment")

# --- 4. Add Control Buttons ---
st.sidebar.header("Controls")

if st.sidebar.button("Run Step"):
    # Run a random step for both robots
    for robot_id in range(len(env.robots)):
        action = env.intelligent_action(robot_id)
        st.session_state.state, reward, done = env.step(robot_id, action)
        robot = st.session_state.state["robots"][robot_id]
        print(robot["position"])
    st.rerun()

if st.sidebar.button("Run Multiple Steps (10)"):
    for _ in range(10):
        for robot_id in range(len(env.robots)):
            action = env.intelligent_action(robot_id)
            st.session_state.state, reward, done = env.step(robot_id, action)
            robot = st.session_state.state["robots"][robot_id]
            print(robot["position"])
        time.sleep(0.1)
    st.rerun()

if st.sidebar.button("Reset Environment"):
    env.reset()
    st.session_state.state = env.get_state()
    st.rerun()

# --- 1. Display Warehouse Grid ---
st.header("1. Warehouse Grid")

# Build the grid (5x5)
grid_size = env.grid_size
grid = [["" for _ in range(grid_size[1])] for _ in range(grid_size[0])]

# Highlight Charging Stations: Mark grid cells (0,0), (4,4)
for cx, cy in env.charging_stations:
    grid[cx][cy] += "C "

# Mark Tasks (P and D)
for task in st.session_state.state["tasks"]:
    if not task["completed"]:
        px, py = task["pickup"]
        grid[px][py] += f"P{task['id']} "
        dx, dy = task["drop"]
        grid[dx][dy] += f"D{task['id']} "

# Mark Robots
for robot in st.session_state.state["robots"]:
    rx, ry = robot["position"]
    grid[rx][ry] += f"R{robot['id']+1} "

# Clean up empty cells to look better in DataFrame
for i in range(grid_size[0]):
    for j in range(grid_size[1]):
        if grid[i][j] == "":
            grid[i][j] = "-"
        else:
            grid[i][j] = grid[i][j].strip()

# Convert grid to DataFrame for display
df_grid = pd.DataFrame(grid)
# Use st.dataframe with custom styling or just raw dataframe
st.dataframe(df_grid, use_container_width=True)

# Layout for Status
col1, col2 = st.columns(2)

# --- 2. Display Robot Status ---
with col1:
    st.header("2. Robot Status")
    for robot in st.session_state.state["robots"]:
        st.info(f"**Robot {robot['id']}** → {robot['position']} | Battery: {robot['battery']} | Carrying: {robot['carrying']}")

# --- 3. Display Task Status ---
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

# --- 5. Show Reward History Graph ---
st.header("5. Reward History Graph")

if os.path.exists("reward_history.json"):
    with open("reward_history.json", "r") as f:
        reward_history = json.load(f)
    
    # Plot Reward vs Episode
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(reward_history, marker='o', linestyle='-', markersize=3, color='royalblue')
    ax.set_title("Reward vs Episode", fontsize=14)
    ax.set_xlabel("Episode", fontsize=12)
    ax.set_ylabel("Reward", fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.7)
    
    st.pyplot(fig)
else:
    st.warning("`reward_history.json` not found in the directory.")
