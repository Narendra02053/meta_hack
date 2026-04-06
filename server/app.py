from fastapi import FastAPI
from server.environment import WarehouseEnv
from server.tasks import easy_task, medium_task, hard_task

app = FastAPI()

# Create environment instance with a default (easy) task
env = WarehouseEnv(easy_task())

TASK_MAP = {
    "easy": easy_task,
    "medium": medium_task,
    "hard": hard_task,
}


@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Warehouse Priority Env API is running"
    }


# REQUIRED: Reset endpoint
@app.api_route("/reset", methods=["GET", "POST"])
def reset(difficulty: str = "easy"):
    global env
    task_fn = TASK_MAP.get(difficulty, easy_task)
    env = WarehouseEnv(task_fn())
    state = env.get_state()
    return {"state": state}



# REQUIRED: Step endpoint
@app.post("/step")
def step(action: dict):
    result = env.step(action["action"])
    state, reward, done, info = result
    return {
        "state": state,
        "reward": reward,
        "done": done,
        "info": info
    }


# REQUIRED: State endpoint
@app.get("/state")
def get_state():
    return env.get_state()