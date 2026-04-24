import sys
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

# Add root directory to path to import warehouse_env
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from warehouse_env import WarehouseEnv

app = FastAPI(title="Warehouse AI Multi-Agent API")

# Persistent environment instance
env = WarehouseEnv()

class StepRequest(BaseModel):
    robot_id: int
    action: str

class RobotState(BaseModel):
    id: int
    position: List[int]
    battery: int
    carrying: bool

class TaskState(BaseModel):
    id: int
    pickup: List[int]
    drop: List[int]
    priority: str
    deadline: int
    assigned: Optional[int]
    completed: bool
    failed: bool

class EnvState(BaseModel):
    robots: List[RobotState]
    tasks: List[TaskState]
    obstacles: List[List[int]]
    congestion_zones: List[List[int]]
    logs: List[str]

@app.get("/")
def read_root():
    return {
        "status": "online",
        "system": "Warehouse Multi-Agent AI",
        "endpoints": ["/state", "/step", "/reset", "/add_task"]
    }

@app.get("/state", response_model=EnvState)
def get_state():
    return env.get_state()

@app.post("/reset", response_model=EnvState)
def reset():
    return env.reset()

@app.post("/step")
def step(request: StepRequest):
    if request.robot_id < 0 or request.robot_id >= len(env.robots):
        raise HTTPException(status_code=400, detail=f"Robot ID {request.robot_id} not found.")
    
    state, reward, done = env.step(request.robot_id, request.action)
    return {
        "state": state,
        "reward": float(reward),
        "done": done
    }

@app.post("/add_task", response_model=EnvState)
def add_task():
    return env.add_random_task()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)