from server.environment import WarehouseEnv
from server.tasks import easy_task, medium_task
from server.grader import calculate_score


def smart_action(env):

    state = env.get_state()

    current_order = state["current_order"]

    priority = state["priority"]

    inventory = state["inventory"]


    # 🚨 URGENT orders first
    if priority == "Urgent" and current_order:

        for product, qty in current_order.items():

            if qty > 0 and inventory.get(product, 0) > 0:

                return f"pick_{product}"


        if all(qty == 0 for qty in current_order.values()):

            if state["packed_orders"] == state["shipped_orders"]:

                return "pack_order"

            else:

                return "ship_order"


    # Normal orders
    if current_order:

        for product, qty in current_order.items():

            if qty > 0:

                if inventory.get(product, 0) > 0:

                    return f"pick_{product}"


        # Pack/Ship logic
        if all(qty == 0 for qty in current_order.values()):

            if state["packed_orders"] == state["shipped_orders"]:

                return "pack_order"

            else:

                return "ship_order"


    # Handle returns smartly
    if state["returns_pending"]:

        return "inspect_return"


    if state["inspection_pending"]:

        product = state["inspection_pending"][0]

        return f"restock_{product}"


    return "wait"



# Run MEDIUM task test
from server.tasks import hard_task

task_config = hard_task()
env = WarehouseEnv(task_config)

env.reset()

done = False

steps = 0

max_steps = 150


while not done and steps < max_steps:

    action = smart_action(env)

    state, reward, done, _ = env.step(action)

    steps += 1


score = calculate_score(env)

print("\nMedium Task Score:", score)