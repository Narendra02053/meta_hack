# Two Robots. One Warehouse. 137% Smarter Than Random.

## The Problem

India's e-commerce industry processes over 10 million orders daily.
Behind every delivery is a warehouse. And inside that warehouse,
someone — or something — is making decisions every second.

Which package goes first? Which robot takes which task? What happens
when an urgent order arrives mid-shift? When does a robot stop to
recharge before it runs out of power three steps from the goal?

Most warehouse systems today answer these questions with fixed rules.
If priority is HIGH, go first. If nearest, go next. Simple logic.

But fixed rules break under pressure.

A HIGH priority task expires while the robot is finishing a LOW
priority one nearby. Two robots race to the same pickup point and
collide. One robot runs out of battery mid-delivery because it
didn't plan ahead.

The movement was fine. The judgment was broken.

This is the problem we set out to solve — not navigation, but
decision-making under uncertainty. Building an environment where
agents could actually learn to make better choices, not just
follow better instructions.

---

## The Solution

We built a multi-agent warehouse simulation where two robots learn
to coordinate, prioritize, and adapt — using a PyTorch Deep
Q-Network as the decision-making brain.

The environment runs on a 5×5 grid. Compact by design, because
tight spaces force harder decisions. Every cell matters.

Inside the grid:
- 2 autonomous robots with position, battery, and task state
- Tasks with HIGH / NORMAL / LOW priority and live deadlines
- Static obstacles representing warehouse shelves
- Charging stations robots must find before battery hits zero
- Emergency task injection mid-simulation
- Peak load mode — multiple tasks injected simultaneously

The PyTorch DQN sits above the environment as a high-level
commander. It reads the warehouse state every step:

- How many tasks are pending?
- What is the highest priority right now?
- What is the minimum deadline remaining?

From those three numbers it decides which strategy the robots run:
Priority-First, Nearest-First, or Deadline-First.

BFS pathfinding then executes the actual movement underneath.

Neural network handles what to focus on.
BFS handles how to get there.

---

## What We Built — The Full Stack

**warehouse_env.py** — Core simulation environment. Handles robot
movement, task management, deadline countdowns, battery drain,
collision detection, BFS pathfinding, and reward calculation.

**rl_agent.py** — PyTorch DQN. 3-layer MLP, Adam optimizer, MSE
loss, experience replay buffer, epsilon-greedy exploration.
Saves trained weights to model.pth.

**train_rl.py** — Training loop. Runs 150 episodes, logs reward
per episode, generates comparison plots against random baseline.
Uses HuggingFace TRL for experiment configuration.

**server/app.py** — FastAPI backend. Exposes GET /state, POST /step,
POST /run, POST /inject_task, GET /history endpoints.

**dashboard.py** — Streamlit frontend. Real-time robot grid,
unit telemetry, fulfillment matrix, strategy monitor, live
reward feed, episode performance summary.

**Deployment** — Docker containerized, hosted on HuggingFace
Spaces, training reproducible via Google Colab.

---

## The Reward System

Every decision has an immediate consequence:

| Event | Reward |
|---|---|
| All tasks complete | +150 |
| Task delivered | +60 |
| Item picked up | +15 |
| Recharged / HIGH priority bonus | +10 |
| Normal movement | -1 |
| Deadline missed | -25 |
| Collision | -20 |
| Obstacle / battery dead | -10 |

This reward signal is what the DQN learned from. And it's what
the live Reward Feed on the dashboard shows in real time — every
+60 and -25 as it happens, color coded green and red.

---

## What Broke During Development

Version 1 used a dictionary Q-table. It worked on easy cases but
collapsed under deadline pressure — too many state combinations,
not enough generalization.

We replaced it with a PyTorch DQN. Neural network generalizes
across unseen states. Immediately better.

Version 1 reward function had a problem. Agents learned to hover
near charging stations collecting easy +10 recharge bonuses while
ignoring deliveries entirely. Classic reward hacking.

We fixed it by making +60 delivery reward dominate everything,
and making -25 deadline penalty expensive enough that ignoring
tasks was never optimal.

Version 1 dashboard showed robot positions only. Judges couldn't
see what the agent was learning or why it was making decisions.

We added the Reward Feed — every action logged with reason and
color. Now you can watch the agent think in real time.

---

## What Improved During Development

| What | Before | After |
|---|---|---|
| Agent type | Dictionary Q-table | PyTorch DQN (3-layer MLP) |
| Training | None | 150 episodes, HF TRL |
| Avg reward | ~400 (random) | ~950 (trained DQN) |
| Improvement | baseline | +137% over random |
| Scores | 0.73 / 0.71 / 0.72 | 0.97 / 0.97 / 0.97 |
| Dashboard | Basic grid | Live reward feed + telemetry |
| Visibility | None | Real-time +/- reward per action |
| Deployment | Local only | HF Space + Docker + FastAPI |

---

## What You See In The Output

Open the live dashboard and run a simulation:

The Tactical Operations Grid shows both robots moving in real
time — picking up packages, navigating around shelves, heading
to charging stations when battery drops.

The Unit Telemetry shows each robot's position, battery level,
and current load status.

The Strategy Monitor shows which strategy the DQN selected —
Priority-First, Nearest-First, or Deadline-First — and why.

The Fulfillment Matrix shows every active task — priority level,
deadline countdown, route, and status.

The Reward Feed shows every single decision as it happens:
+60 green when a delivery completes, -25 red when a deadline
is missed, -1 gray for every movement step.

The Episode Performance Summary shows total tasks completed,
tasks expired, emergency tasks saved, coordination score, and
final efficiency score.

![Dashboard Preview](images/dashboard_preview.png)
*Live reward feed showing agent decisions in real time*

![Peak Load Grid](images/performance_metrics.png)
*Tactical Operations Grid under festival-level peak demand*

---

## Training Evidence

Early episodes are chaotic. The agent tries random strategies,
fails, gets penalized. Around episode 40-50 it starts learning
that deadline pressure beats proximity. By episode 100 it
consistently picks Deadline-First under stress.

Random baseline: ~400 average reward
Trained DQN: ~950 average reward
Improvement: +137%

Final scores: Easy 0.97 / Medium 0.97 / Hard 0.97

---

## System Architecture

![Architecture Diagram](images/architecture_diagram.png)

The full stack:
- Streamlit dashboard with live reward feed and robot telemetry
- FastAPI backend managing all simulation state
- PyTorch DQN neural policy engine (model.pth)
- HuggingFace TRL for training configuration
- Docker containerized deployment
- HuggingFace Spaces for live hosting

---

## Why It Matters

This environment teaches agents something real warehouses need
every day — how to make good decisions under pressure, with
incomplete information, against a ticking clock.

The same problem exists at scale in Amazon fulfillment centers,
Flipkart warehouses, Zomato dark stores, and every last-mile
logistics hub in India.

We built a training ground for that problem. An environment where
agents fail, learn, adapt, and get measurably better — provably,
with numbers, reproducibly in a Colab notebook anyone can run.

---

## Try It

Live Dashboard:
https://huggingface.co/spaces/kottakur/warehouse-priority-env

Training Notebook (PyTorch DQN + HuggingFace TRL):
https://colab.research.google.com/drive/1yAKAoVT_yDQAVVhbNvQhS7oqloQkm9nI#scrollTo=oB1JUzXufsB3

GitHub:
https://github.com/Narendra02053/meta_hack

Built for the Meta × PyTorch × HuggingFace OpenEnv Hackathon.
By Narendra — AMC Engineering College, Bengaluru.
