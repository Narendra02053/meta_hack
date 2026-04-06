---
title: Warehouse Priority Env
emoji: 📦
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
tags:
- openenv
- supply-chain
- reinforcement-learning
- logistics
---

# 📦 Warehouse Priority Environment (OpenEnv)

[![Hugging Face Space](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Space-blue)](https://huggingface.co/spaces/kottakur/warehouse-priority-env)
[![OpenEnv Spec](https://img.shields.io/badge/OpenEnv-Compliant-green)](https://github.com/OpenEnv/spec)

A high-fidelity logistics simulation for evaluating AI agents on real-world warehouse operations, including **Inventory Management**, **Order Fulfillment**, **Deadline Prioritization**, and **Returns Processing**.

---

## 🚀 Motivation
Modern e-commerce requires highly efficient warehouse systems that can handle thousands of items, prioritize urgent shipments, and manage reverse logistics (returns) seamlessly. This environment provides a platform to train and evaluate agents on these complex, multi-objective tasks.

---

## 🧠 Environment Design

### 🔭 Observation Space
The state is exposed via a typed Pydantic `Observation` model:
- `inventory` (Dict[str, int]): Current stock levels for all products.
- `current_order` (Optional[Dict[str, int]]): Items and quantities required for the active order.
- `current_deadline` (Optional[int]): Remaining steps before the active order is considered late.
- `priority` (str): `"Normal"` or `"Urgent"` (escalates when deadline ≤ 3).
- `returns_pending` (List[str]): List of items waiting to be processed from customer returns.
- `inspection_pending` (List[str]): List of items in the inspection bay waiting to be restocked.
- `packed_orders` (int): Count of orders picked and packed, ready for shipping.
- `shipped_orders` (int): Count of orders successfully dispatched.
- `time_left` (int): Global episode time remaining.

### 🎮 Action Space
The agent can execute following actions:
| Action | Description | Reward Logic |
| :--- | :--- | :--- |
| `pick_<item>` | Pick a specific item from `inventory` for the current order. | +0.2 (Success), -0.3 (Fail) |
| `pack_order` | Pack the current order once all items are picked. | +0.3 (Success), -0.3 (Fail) |
| `ship_order` | Ship the latest packed order. | +0.5 to +1.0 (Depends on Deadline) |
| `inspect_return` | Process an item from `returns_pending` to `inspection_pending`. | +0.2 (Success), -0.2 (Fail) |
| `restock_<item>` | Move an item from `inspection_pending` to `inventory`. | +0.3 (Success), -0.2 (Fail) |
| `wait` | Skip a turn (consumes time). | -0.1 penalty |

---

## 🎯 Task Scenarios & Baseline Scores

| Task ID | Difficulty | Orders | Time | Description | **Baseline Score** |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Easy** | 🟢 Easy | 3 | 20 | Small inventory, focus on basic flow. | **0.95+** |
| **Medium**| 🟡 Medium | 6 | 30 | Adds returns processing and multitasking. | **0.95+** |
| **Hard**  | 🔴 Hard | 10 | 40 | High volume, tight deadlines, complex returns. | **0.95+** |

---

## 🚦 Getting Started

### 1. Local Installation
```bash
git clone https://github.com/Narendra02053/meta_hack.git
cd meta_hack
python -m venv venv
source venv/bin/activate  # venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 2. Run the Server
```bash
uvicorn server.app:app --host 0.0.0.0 --port 7860
```

### 3. Run Baseline Inference
```bash
# Uses the built-in SmartAgent (Reproducible Baseline)
python inference.py
```

To run with an LLM (e.g., GPT-4), set your API key:
```bash
export OPENAI_API_KEY="your-key"
python inference.py
```

---

## 📐 OpenEnv Specification Compliance
- ✅ **Typed Models**: Full Pydantic schemas for `Observation`, `Action`, and `StepResponse`.
- ✅ **Standard API**: Implements `/reset`, `/step`, and `/state` endpoints.
- ✅ **Configuration**: Guided by `openenv.yaml` at the root.
- ✅ **Reproducibility**: `inference.py` ensures consistent baseline evaluation.
- ✅ **Containerized**: Production-ready `Dockerfile` for Hugging Face Spaces.

---

## 🧱 Project Structure
```text
.
├── server/
│   ├── app.py          # FastAPI Server & Routes
│   ├── environment.py  # Warehouse Core Logic
│   ├── schema.py       # Pydantic Typing (Action/Obs)
│   ├── grader.py       # Deterministic Scorer
│   ├── model.py        # SmartAgent Heuristics
│   └── tasks.py        # Task Configurations
├── openenv.yaml        # Spec Metadata
├── inference.py        # Baseline Inference Client
├── Dockerfile          # Container Config
└── README.md           # Documentation
```

---

## 👤 Author
**Narendra**  
[nn7116580@gmail.com](mailto:nn7116580@gmail.com)  

Developed for the **OpenEnv Hackathon**.