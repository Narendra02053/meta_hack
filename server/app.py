from fastapi import FastAPI
from server.environment import WarehouseEnv

app = FastAPI()

# Create environment instance
env = WarehouseEnv()


@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Warehouse Priority Env API is running"
    }


# REQUIRED: Reset endpoint
@app.post("/reset")
def reset():
    state = env.reset()
    return {"state": state}


# REQUIRED: Step endpoint
@app.post("/step")
def step(action: dict):
    result = env.step(action)
    return result


# REQUIRED: State endpoint
@app.get("/state")
def get_state():
    return env.state()