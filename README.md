---
title: Warehouse Priority Env
emoji: 📦
colorFrom: blue
colorTo: indigo
sdk: streamlit
app_file: dashboard.py
app_port: 7860
pinned: false
tags:
- openenv
- pytorch
- meta
- multi-agent
- reinforcement-learning
- logistics
---

# 📦 Multi-Agent Warehouse Intelligence System (MAWIS)

### **Meta × PyTorch × HuggingFace OpenEnv Hackathon — Grand Finale Edition**

[![PyTorch](https://img.shields.io/badge/PyTorch-%23EE4C2C.svg?style=for-the-badge&logo=PyTorch&logoColor=white)](https://pytorch.org/)
[![HuggingFace](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-yellow?style=for-the-badge)](https://huggingface.co/spaces/kottakur/warehouse-priority-env)

## 🎯 Executive Summary
MAWIS is an advanced multi-agent reinforcement learning environment designed for high-pressure logistics optimization. Unlike static simulations, MAWIS uses a **PyTorch-driven Deep Q-Network (DQN)** to dynamically switch between operational strategies based on real-time environmental stress, achieving a consistent **0.97 performance score** across complex edge cases.

---

## 🧠 Core Intelligence: The PyTorch DQN Brain
The system's "Commander" is a Deep RL agent built using **PyTorch**. 

- **Architecture**: 3-layer MLP (32x32 hidden units) with ReLU activation.
- **State Space**: 3D vector representing `[Pending Tasks, Max Priority, Min Deadline]`.
- **Action Space**: Strategy Selection — `[Priority-First, Nearest-First, Deadline-First]`.
- **Optimization**: Adam optimizer with MSE loss, training across 150+ episodes to achieve peak operational stability.

### 📈 Learning Progress
Our PyTorch agent demonstrates significant performance gains over heuristic baselines:
- **DQN Efficiency**: ~950+ average reward.
- **Random Baseline**: ~400 average reward.
- **Improvement**: **+137% performance boost** through neural strategy selection.

---

## 🚀 Live Deployment & Visuals

🔗 **Interactive Dashboard (Hugging Face)**: [Launch Project](https://huggingface.co/spaces/kottakur/warehouse-priority-env)  
🔗 **Reproducible Research (Google Colab)**: [View Notebook](https://colab.research.google.com/drive/1hmpR4uRP3JKv2_xNEKLdOlbC5adH1zQ2)  

---

## 🏗️ Technical Architecture
MAWIS implements a decoupled, high-performance architecture:
1. **Frontend**: Streamlit-based Glassmorphism dashboard with real-time PyTorch inference telemetry.
2. **Environment**: Custom discrete grid-world simulation with multi-agent collision physics.
3. **Logic**: BFS-based low-level pathfinding guided by high-level RL strategy selection.
4. **Backend**: FastAPI endpoints for remote inference and automated grading.

---

## 🚦 Key Logistics Constraints
To ensure real-world relevance, the environment models:
- **Task Urgency**: Dynamic HIGH/NORMAL/LOW priority mapping.
- **Temporal Pressure**: Real-time deadline decay with penalty-heavy failures.
- **Resource Limits**: Autonomous battery management and recharging cycles.
- **Spatial Constraints**: Multi-agent congestion zones and static obstacles.
- **Peak Load Stress**: On-demand "Emergency Injection" for stress testing.

---

## 📂 Project Structure
```text
meta_hack/
├── warehouse_priority_env/
│   └── grid_env.py      # Core Simulation Logic
├── rl_agent.py          # PyTorch DQN Implementation [THE BRAIN]
├── train_rl.py          # PyTorch Training Loop & Comparison Logic
├── dashboard.py         # Streamlit Glassmorphism UI
├── model.pth            # Saved PyTorch Weights
├── blog.md              # Technical Narrative & Impact Analysis
└── README.md            # Technical Documentation
```

---

## 📊 Final Performance Metrics
| Metric | Result | Insight |
| :--- | :--- | :--- |
| **Easy Score** | **0.97** | Flawless task completion under low load. |
| **Medium Score** | **0.97** | Efficient coordination with moderate obstacles. |
| **Hard Score** | **0.97** | Adaptive strategy switching under peak load. |
| **Throughput** | **12.5** | High task-per-step ratio. |

---

## 👨‍💻 Developed by Narendra
**Finalist - Meta × PyTorch OpenEnv Hackathon**  
*Building the future of autonomous logistics with PyTorch.*
