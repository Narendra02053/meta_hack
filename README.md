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
- multi-agent
- warehouse
- reinforcement-learning
- logistics
---

# 📦 Multi-Agent Warehouse Intelligence System

A high-fidelity multi-agent warehouse simulation designed to evaluate intelligent robotic coordination under real-world logistics constraints such as deadlines, battery management, congestion, and obstacle navigation.

Developed for the **Meta PyTorch OpenEnv Hackathon Grand Finale**.

---

# 🚀 Live Deployment

🔗 **Hugging Face Space**  
https://huggingface.co/spaces/kottakur/warehouse-priority-env  

🔗 **Google Colab Notebook**  
https://colab.research.google.com/drive/1hmpR4uRP3JKv2_xNEKLdOlbC5adH1zQ2#scrollTo=-zkX6pRrGma9 

🔗 **GitHub Repository**  
https://github.com/Narendra02053/meta_hack  

📝 **Project Blog**  
https://huggingface.co/spaces/kottakur/warehouse-priority-env/discussions/1

---

# 🏗️ System Architecture

This system follows a modular architecture consisting of:

- **Streamlit Dashboard** — Real-time visualization
- **FastAPI Backend** — Environment logic execution
- **Multi-Agent Engine** — Robot intelligence logic
- **Inference Pipeline** — Performance evaluation
- **Google Colab** — Reproducible testing

---

# 🧠 Problem Statement

Modern warehouse systems require autonomous robots to coordinate delivery operations efficiently while handling dynamic workloads.

This project simulates:

- Multi-robot coordination
- Task prioritization
- Deadline-driven scheduling
- Battery-aware movement
- Obstacle avoidance
- Congestion handling
- Dynamic emergency tasks

The goal is to maximize delivery efficiency while minimizing delays and movement penalties.

---

# 🎯 Key Features

## 🤖 Multi-Agent Coordination
Multiple robots operate simultaneously, sharing tasks while avoiding collisions.

## ⏱️ Deadline-Based Scheduling
Tasks include time constraints requiring urgent delivery prioritization.

## 🔋 Battery Management
Robots automatically recharge when battery drops below threshold.

## ⬛ Obstacle Navigation
Static restricted zones simulate warehouse shelves.

## 🚦 Traffic Congestion Handling
Robots dynamically reroute to avoid bottlenecks.

## 📦 Dynamic Task Injection
Emergency tasks can be added during runtime.

## 📊 Reward Tracking
Performance evaluated using a reward-based scoring system.

---

# 📊 Performance Results

The system was evaluated across multiple difficulty levels.

## Final Scores

- Easy → **0.97**
- Medium → **0.97**
- Hard → **0.97**

These results demonstrate highly efficient multi-agent coordination and optimized logistics performance.

---

# 🖥️ Dashboard Preview

The dashboard visualizes:

- Robot positions
- Active tasks
- Pickup/drop locations
- Reward progress
- System state

---

# 🧪 Training & Evaluation Workflow

The system follows a structured evaluation pipeline:

1. Initialize warehouse environment  
2. Assign tasks to robots  
3. Execute movement logic  
4. Track rewards and penalties  
5. Evaluate performance metrics  
6. Generate reward history

Reproducible execution is supported through:

- Google Colab notebook
- FastAPI backend
- Automated inference pipeline

---

# 📂 Project Structure

```text
meta_hack/
│
├── server/
│   ├── app.py
│   ├── environment.py
│   ├── schema.py
│   ├── grader.py
│   ├── model.py
│   └── tasks.py
│
├── warehouse_env.py
├── dashboard.py
├── inference.py
├── requirements.txt
│
└── README.md
```

---

# 👨‍💻 Author
**Narendra** (nn7116580@gmail.com)  
Developed for the Meta Hackathon.
