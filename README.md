---
title: Multi-Agent Warehouse Intelligence
emoji: 🤖
colorFrom: blue
colorTo: blue
sdk: streamlit
app_file: dashboard.py
app_port: 7860
pinned: false
tags:
- logistics
- multi-agent
- simulation
- warehouse
- intelligent-agents
---

# Multi-Agent Warehouse Intelligence Simulation

This project is a high-performance simulation for evaluating multi-agent coordination in dynamic warehouse environments. It includes a Streamlit-based dashboard for visualization and a FastAPI-based backend for programmatic interaction.

## Deployment Links

### Hugging Face Space
https://huggingface.co/spaces/kottakur/warehouse-priority-env

### Google Colab Notebook
https://colab.research.google.com/drive/1tVkSTpQe7pAhafIc_QOOcQ1y4uMdnK2o

### Hugging Face Blog
https://huggingface.co/spaces/kottakur/warehouse-priority-env/discussions/1

### GitHub Repository
https://github.com/Narendra02053/meta_hack

---

## Key Features

### Coordination and Intelligence
- Decentralized Intelligence: Each agent evaluates its own actions independently.
- Priority-Aware Scheduling: Tasks are ranked by importance (High, Normal, Low).
- Deadline Sensitivity: Agents prioritize tasks based on remaining time to failure.

### Navigation and Constraints
- Obstacle Avoidance: Automated routing around static warehouse shelves and restricted zones.
- Traffic Congestion: Real-time detection of robot density with dynamic slowdown and rerouting.
- Energy Management: Automated battery level tracking and charging station prioritization.

### Analytics and Control
- Real-time Telemetry: Live monitoring of robot positions and task status.
- Performance Metrics: Efficiency scores and reward history tracking.
- Dynamic Tasking: Ability to inject emergency tasks into the simulation in real-time.

---

## Installation and Setup

### 1. Install Dependencies
```bash
git clone https://github.com/Narendra02053/meta_hack.git
cd meta_hack
pip install -r requirements.txt
```

### 2. Run the Dashboard
The dashboard provides a visual interface for the simulation.
```bash
streamlit run dashboard.py
```

### 3. Run the Backend API
The FastAPI server allows for programmatic control.
```bash
uvicorn server.app:app --host 0.0.0.0 --port 7860
```

---

## API Documentation

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| /state | GET | Get current grid, robot, and task state. |
| /step | POST | Execute an action for a specific robot. |
| /reset | POST | Reset the environment. |
| /add_task | POST | Add a new random task to the grid. |

---

## Project Structure
- dashboard.py: Streamlit visualization engine.
- warehouse_env.py: Core multi-agent simulation logic.
- server/app.py: FastAPI REST interface.
- reward_history.json: Persistence for episode performance.

---

## Contact
Narendra (nn7116580@gmail.com)

Developed for the Meta Hackathon.