---
title: Warehouse Priority Env
emoji: 📦
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# 📦 Warehouse Priority Environment


A real-world inspired warehouse simulation environment built using **OpenEnv** standards. 

This project models realistic logistics workflows such as inventory tracking, order processing, return handling, and deadline-based delivery prioritization. The environment is designed to simulate complex warehouse operations where intelligent agents must make efficient decisions under time constraints.

---

## 🚀 Project Overview

Modern warehouses process thousands of orders daily. Managing inventory, shipping deadlines, and return workflows requires optimized decision-making systems. The **Warehouse Priority Environment** simulates these real-world logistics operations in a structured environment, allowing agents to:

- ✅ **Manage dynamic inventory levels**
- ✅ **Process customer orders**
- ✅ **Handle return workflows**
- ✅ **Meet strict shipping deadlines**
- ✅ **Handle priority escalation logic**
- ✅ **Optimize operational efficiency**

This environment helps test intelligent decision-making models in logistics and supply chain domains.

---

## 🧠 Core Features

### 📦 Inventory Management
Tracks multiple product types and dynamically updates stock levels based on actions.

### 📬 Order Processing
Agents must pick correct items, pack them, and ship orders sequentially.

### ⏱️ Deadline-Based Processing
Orders include delivery deadlines that impact reward calculations.

### 🔥 Priority Escalation
Orders automatically escalate to **Urgent** priority when deadlines become critical (≤ 3 seconds).

### 🔄 Returns Handling
Returned items must be inspected and restocked before they can be reused.

### 🎯 Multi-Difficulty Tasks
Supports three difficulty levels:
- **Easy** → Low order volume
- **Medium** → Moderate complexity
- **Hard** → High order volume with strict deadlines

---

## 🛠️ Tech Stack

- **Programming Language**: Python 3.11
- **API Framework**: FastAPI
- **Server**: Uvicorn
- **Environment Standard**: OpenEnv
- **Containerization**: Docker
- **Deployment Platform**: Hugging Face Spaces

---

## 🧱 Project Structure

```text
meta_hack/
│
├── server/
│   ├── app.py              # FastAPI endpoints (Standardized)
│   ├── environment.py      # Core warehouse logic
│   ├── grader.py           # Performance evaluation logic
│   ├── model.py            # Agent behavior logic
│   ├── tasks.py            # Task difficulty definitions
│
├── openenv.yaml            # REQUIRED: Root configuration file
├── configs/
│   └── openenv.yml         # Backup configuration
│
├── client/
│   └── run_agent.py        # Sample agent interaction
│
├── inference.py            # Required OpenEnv test script
├── test_env.py             # Local testing script
├── Dockerfile              # Container setup
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

---

## 🚦 API Endpoints

This environment exposes REST API endpoints compatible with OpenEnv specifications.

### 1️⃣ Reset Environment
`GET/POST /reset`
Resets the environment to its initial state.

**Optional Input (JSON):**
```json
{
  "difficulty": "easy"
}
```
*Available levels: `easy`, `medium`, `hard`*

---

### 2️⃣ Execute Action
`POST /step`
Executes an action inside the environment.

**Request (JSON):**
```json
{
  "action": "pick_product"
}
```
**Supported Actions:**
`pick_product`, `pack_order`, `ship_order`, `inspect_return`, `restock_product`, `wait`

---

### 3️⃣ Get Current State
`GET /state`
Returns the current environment state without advancing time.

---

## 💻 Local Setup Instructions

### Step 1 — Create Virtual Environment
```bash
python -m venv venv
```
**Activate (Windows):**
```bash
.\venv\Scripts\activate
```

### Step 2 — Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3 — Run Server
```bash
uvicorn server.app:app --host 0.0.0.0 --port 7860
```
*Server will run at: `http://localhost:7860`*

### Step 4 — Run Inference Test
```bash
python inference.py
```

---

## 🐳 Docker Deployment
The environment is fully containerized.

**Build Docker Image:**
```bash
docker build -t warehouse-env .
```

**Run Docker Container:**
```bash
docker run -p 7860:7860 warehouse-env
```

---

## ☁️ Hugging Face Deployment
This project is deployed using **Hugging Face Spaces**.

**Public Space URL:**
[https://huggingface.co/spaces/kottakur/warehouse-priority-env](https://huggingface.co/spaces/kottakur/warehouse-priority-env)

---

## 🧪 OpenEnv Compliance
- **Configuration File**: `openenv.yaml` (at repo root)
- **Entrypoint**: `server.environment:WarehouseEnv`
- **Supported Tasks**: `easy`, `medium`, `hard`

---

## 👤 Author
**Narendra**

- **GitHub Repository**: [https://github.com/Narendra02053/meta_hack](https://github.com/Narendra02053/meta_hack)
- **Hugging Face Space**: [https://huggingface.co/spaces/kottakur/warehouse-priority-env](https://huggingface.co/spaces/kottakur/warehouse-priority-env)

---

## 📜 License
This project is developed for educational and hackathon purposes. Use is permitted for learning and experimentation.