from fastapi import FastAPI

from server.tasks import (
    easy_task,
    medium_task,
    hard_task
)

from server.environment import WarehouseEnv
from server.grader import calculate_score


app = FastAPI()


# -----------------------------
# TASKS ENDPOINT
# -----------------------------

@app.get("/tasks")

def get_tasks():

    return {

        "easy": easy_task(),

        "medium": medium_task(),

        "hard": hard_task()

    }


# -----------------------------
# BASELINE AGENT
# -----------------------------

def run_smart_agent(task_config):

    env = WarehouseEnv(task_config)

    env.reset()

    done = False

    steps = 0

    max_steps = 100


    while not done and steps < max_steps:

        state = env.get_state()

        current_order = state["current_order"]

        priority = state["priority"]


        if current_order:

            for product, qty in current_order.items():

                if qty > 0:

                    action = f"pick_{product}"

                    break

            else:

                if state["packed_orders"] == state["shipped_orders"]:

                    action = "pack_order"

                else:

                    action = "ship_order"

        elif state["returns_pending"]:

            action = "inspect_return"

        elif state["inspection_pending"]:

            product = state["inspection_pending"][0]

            action = f"restock_{product}"

        else:

            action = "wait"


        state, reward, done, _ = env.step(action)

        steps += 1


    score = calculate_score(env)

    return score


# -----------------------------
# BASELINE ENDPOINT
# -----------------------------

@app.get("/baseline")

def baseline():

    task_config = easy_task()

    score = run_smart_agent(task_config)

    return {

        "baseline_score": score

    }


# -----------------------------
# GRADER ENDPOINT
# -----------------------------

@app.get("/grader")

def grader():

    task_config = medium_task()

    score = run_smart_agent(task_config)

    return {

        "grader_score": score

    }