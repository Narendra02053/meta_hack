# 📦 Warehouse Priority Environment

A professional real-world warehouse simulation environment designed for building and testing agentic AI models. The environment simulates a fast-paced logistics hub where agents must manage inventory, process customer orders, handle returns, and meet strict delivery deadlines through dynamic priority escalation.

## 🚀 Overview

The **Warehouse Priority Env** challenges agents to optimize warehouse operations. It includes comprehensive features such as:
- **Dynamic Inventory Management**: Keep track of product levels and restock failed returns.
- **Order Picking & Packing**: Accurate picking and packing of multi-item customer orders.
- **Deadline-Based Shipping**: Priority-based rewards for meeting delivery windows.
- **Priority Escalation**: Automatic triggers for "Urgent" status when deadlines are short (≤ 3 seconds).
- **Return Processing**: Inspect and restock returned items into the inventory.

---

## 🛠️ Tech Stack

- **Core**: Python 3.11
- **API Framework**: FastAPI & Uvicorn
- **Observation Space**: Discrete status metrics (Inventory, Deadlines, Order Queues)
- **Deployment**: Dockerized for Hugging Face Spaces

---

## 🚦 API Reference

The environment is served as a REST API. All endpoints are compatible with the **OpenEnv** standard.

### 1. Reset Environment
`GET/POST /reset`
Resets the simulation to the initial state.
- **Parameters**: `difficulty` (string: `easy`, `medium`, `hard`) - *Default: easy*
- **Response**: `{ "state": { ... } }`

### 2. Take a Step
`POST /step`
Executes an action in the environment.
- **Body**: `{ "action": "action_name" }`
- **Actions**:
    - `pick_<product>`: Pick a product for the current order.
    - `pack_order`: Finalize the current items into a package.
    - `ship_order`: Ship the packet and advance to the next order.
    - `inspect_return`: Move an item from returns to inspection.
    - `restock_<product>`: Move an inspected item back to inventory.
    - `wait`: Skip a time cycle.
- **Response**: `{ "state": { ... }, "reward": float, "done": boolean, "info": { ... } }`

### 3. Get Current State
`GET /state`
Returns the full current state without advancing time.

---

## 💻 Local Setup & Usage

### 1. Installation
Clone the repository and install dependencies:
```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Running the Server
Start the environment API locally on port 7860:
```bash
uvicorn server.app:app --host 0.0.0.0 --port 7860
```

### 3. Running Inference
Test the environment using the provided inference script:
```bash
python inference.py
```

---

## 🐳 Docker Deployment

The environment is fully dockerized. To build and run manually:
```bash
docker build -t warehouse-env .
docker run -p 7860:7860 warehouse-env
```

## 🏆 OpenEnv Validation

This repository is compliant with the **OpenEnv** specification.
- **Config File**: `openenv.yaml`
- **Entrypoint**: `server.environment:WarehouseEnv`
- **Tasks**: Easy, Medium, and Hard variations available.

---

## 📧 Contact & Support
For help or collaboration, please reach out via GitHub or context-specific hackathon support channels.