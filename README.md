---
title: Multi-Agent Warehouse Intelligence
emoji: 🤖
colorFrom: blue
colorTo: blue
sdk: streamlit
app_port: 7860
pinned: false
tags:
- logistics
- multi-agent
- simulation
- warehouse
- intelligent-agents
---

# 🏭 Multi-Agent Warehouse Intelligence Simulation

[![Hugging Face Space](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Space-blue)](https://huggingface.co/spaces/kottakur/warehouse-priority-env)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A high-performance, real-time simulation for evaluating multi-agent coordination in dynamic warehouse environments. Built with **Streamlit** for visualization and **FastAPI** for programmatic interaction.

---

## 🚀 Key Features

### 🧠 Intelligent Coordination
- **Decentralized Intelligence**: Agents independently evaluate the environment to determine optimal actions.
- **Priority-Aware Scheduling**: Tasks are ranked by priority (**HIGH**, **NORMAL**, **LOW**).
- **Deadline Sensitivity**: Automated rerouting based on task expiration urgency.

### 🚦 Realistic Navigation
- **Obstacle Avoidance**: Agents navigate around static shelves and restricted zones (⬛).
- **Traffic Congestion Control**: Real-time detection of robot density with dynamic slowdown (🟠).
- **Energy Management**: Automatic battery tracking and prioritization of charging stations (🔋).

### 📊 Observability & Control
- **Live Telemetry**: Real-time fleet tracking and task fulfillment monitoring.
- **Performance Analytics**: Automated "Efficiency Score" and reward history visualization.
- **Dynamic Injection**: Ability to inject emergency tasks during live simulations.

---

## 🛠️ Getting Started

### 1. Installation
```bash
git clone https://github.com/Narendra02053/meta_hack.git
cd meta_hack
pip install -r requirements.txt
```

### 2. Running the System
The project consists of two main components:

#### **A. Run the Dashboard (Streamlit)**
Visualizes the warehouse grid, agent movements, and performance metrics.
```bash
streamlit run dashboard.py
```

#### **B. Run the Backend API (FastAPI)**
Exposes the environment for programmatic control and testing.
```bash
uvicorn server.app:app --host 0.0.0.0 --port 7860
```

---

## 📡 API Endpoints

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/state` | `GET` | Retrieve the current grid, agent, and task states. |
| `/step` | `POST` | Execute an action for a specific robot. |
| `/reset` | `POST` | Reset the environment to initial conditions. |
| `/add_task` | `POST` | Inject a new randomized task into the grid. |

---

## 🧱 Project Structure
```text
.
├── dashboard.py         # Main UI & Visualization Engine
├── warehouse_env.py     # Simulation Core & Multi-Agent Logic
├── server/
│   └── app.py           # FastAPI REST Interface
├── reward_history.json  # Persistence for performance metrics
├── requirements.txt     # System dependencies
└── README.md            # Project documentation
```

---

## 👤 Author
**Narendra**  
[nn7116580@gmail.com](mailto:nn7116580@gmail.com)  

Developed for the **Meta Hackathon**.