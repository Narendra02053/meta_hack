---
title: Multi-Agent Warehouse Intelligence (MAWI)
emoji: 🤖
colorFrom: indigo
colorTo: indigo
sdk: streamlit
app_file: dashboard.py
app_port: 7860
pinned: true
tags:
  - logistics
  - multi-agent
  - navigation
  - automation
  - smart-cities
---

# 🏭 Multi-Agent Warehouse Intelligence (MAWI)
### *Elite Autonomous Logistics & Pathfinding Simulation*

[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-yellow)](https://huggingface.co/spaces/kottakur/warehouse-priority-env)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

## 📌 Executive Summary
**MAWI** is a high-fidelity logistics simulation engine designed to evaluate decentralized multi-agent coordination within dynamic, constrained environments. Developed with a focus on real-world industrial constraints, the system integrates advanced pathfinding, congestion awareness, and priority-weighted scheduling to optimize fulfillment cycles.

The platform provides a dual-layer interface: a **Streamlit Tactical Dashboard** for real-time visualization and a **FastAPI REST Backbone** for programmatic agent control and high-throughput evaluation.

---

## 🚀 Quick Links & Deployment

You can interact with the simulation or run evaluations using the links below:

*   **[Interactive Dashboard (Hugging Face)](https://huggingface.co/spaces/kottakur/warehouse-priority-env)** - Live visualizer with real-time telemetry.
*   **[Google Colab Evaluation Notebook](https://colab.research.google.com/drive/1hmpR4uRP3JKv2_xNEKLdOlbC5adH1zQ2#scrollTo=-zkX6pRrGma9)** - Complete environment for running scores and benchmarks.
*   **[Hugging Face Discussion](https://huggingface.co/spaces/kottakur/warehouse-priority-env/discussions/1)** - Project background and implementation details.
*   **[GitHub Repository](https://github.com/Narendra02053/meta_hack)** - Full source code and documentation.

---

## 📈 Performance Benchmarks (v2.5 Elite)

The system is engineered for **90+ Performance Ratings** using an ultra-lean operational strategy that minimizes idling and maximizes time-efficiency bonuses.

| Metric | Easy | Medium | Hard |
| :--- | :--- | :--- | :--- |
| **Efficiency Score** | **0.97** | **0.97** | **0.97** |
| **Fulfillment Rate** | 100% | 100% | 100% |
| **Avg. Cycle Time** | 3.3 steps/task | 3.8 steps/task | 2.9 steps/task |

### **Optimization Rationale**
- **Zero-Waste Pathing**: Agents utilize a strictly prioritized BFS (Breadth-First Search) protocol that treats time as the most expensive resource.
- **Proactive Inventory Flow**: Implemented a predictive auto-restocking engine that maintains zero-latency inventory availability for high-demand SKUs.
- **Dynamic Congestion Mitigation**: Real-time traffic density monitoring with automated rerouting to prevent gridlock in high-traffic corridors.

---

## 🛠️ Core Architecture & Intelligence

### 1. Navigation Engine
- **BFS Pathfinding**: Mathematically optimal shortest-path calculation in grid-based environments.
- **Collision Avoidance**: Predictive logic to avoid static obstacles (shelves) and dynamic obstacles (other agents).
- **Traffic Density Tracking**: Heatmap-style detection of bottleneck areas with dynamic slowdown modifiers.

### 2. Decision Logic
- **Decentralized Autonomy**: Each unit independently calculates its state-action vector based on localized and global telemetry.
- **Priority-Weighted Heuristics**: Multi-objective optimization focusing on Task Priority (High/Normal/Low) and Deadline Criticality.
- **Energy Conservation**: Automated state-switching to charging protocols when battery thresholds are breached.

---

## 💻 Technical Stack
- **Engine**: Python 3.11, Gymnasium-style Environment
- **Visualization**: Streamlit (Elite Tactical UI with Glassmorphism)
- **API Framework**: FastAPI (Asynchronous REST Backend)
- **Logistics Algorithms**: BFS (Breadth-First Search), Decentralized Task Allocation

---

## 🛠️ Installation & Rapid Start

### Development Environment Setup
```bash
# Clone the repository
git clone https://github.com/Narendra02053/meta_hack.git
cd meta_hack

# Initialize environment & dependencies
pip install -r requirements.txt
```

### Execution Protocols
- **Tactical Visualizer**: `streamlit run dashboard.py`
- **Programmatic Server**: `python server/app.py`
- **Benchmark Evaluator**: `python inference.py`

---

## 📡 API Reference

| Endpoint | Method | Payload | Description |
| :--- | :--- | :--- | :--- |
| `/state` | `GET` | N/A | Full environment telemetry (Grid, Robots, Tasks) |
| `/step` | `POST` | `{"action": str}` | Execute agent action and receive updated observation |
| `/reset` | `POST` | `{"difficulty": str}` | Re-initialize environment to specific complexity |
| `/grader` | `GET` | N/A | Retrieve real-time performance and efficiency score |

---

## 👨‍💻 Author & Acknowledgments
**Narendra** | Elite Software Engineer & AI Architect
[Email](mailto:nn7116580@gmail.com) | [GitHub](https://github.com/Narendra02053)

*Developed for the **Meta Hackathon**, pushing the boundaries of autonomous logistics intelligence.*