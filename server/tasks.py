import random


# -------------------------
# PRODUCT LIST
# -------------------------

PRODUCTS = [

    "phone",
    "laptop",
    "tablet",
    "headphones",
    "charger",
    "mouse",
    "keyboard",
    "camera",
    "speaker",
    "monitor",
    "printer",
    "router"

]


# -------------------------
# HELPER FUNCTIONS
# -------------------------

def generate_inventory(size):

    inventory = {}

    selected = random.sample(
        PRODUCTS,
        size
    )

    for product in selected:

        inventory[product] = random.randint(
            5,
            15
        )

    return inventory



def generate_orders(inventory, num_orders):

    orders = []

    products = list(inventory.keys())

    for _ in range(num_orders):

        order = {}

        num_items = random.randint(
            1,
            3
        )

        selected = random.sample(
            products,
            num_items
        )

        for p in selected:

            order[p] = random.randint(
                1,
                2
            )

        orders.append(order)

    return orders



def generate_returns(inventory, num_returns):

    products = list(inventory.keys())

    return random.sample(
        products,
        num_returns
    )


# -------------------------
# EASY TASK
# -------------------------

def easy_task():

    inventory = generate_inventory(5)

    orders = generate_orders(
        inventory,
        3
    )

    returns = generate_returns(
        inventory,
        1
    )

    return {

        "inventory": inventory,

        "orders": orders,

        "returns": returns,

        "workers": 1,

        "time": 20

    }


# -------------------------
# MEDIUM TASK
# -------------------------

def medium_task():

    inventory = generate_inventory(8)

    orders = generate_orders(
        inventory,
        6
    )

    returns = generate_returns(
        inventory,
        2
    )

    return {

        "inventory": inventory,

        "orders": orders,

        "returns": returns,

        "workers": 2,

        "time": 30

    }


# -------------------------
# HARD TASK
# -------------------------

def hard_task():

    inventory = generate_inventory(10)

    orders = generate_orders(
        inventory,
        10
    )

    returns = generate_returns(
        inventory,
        4
    )

    return {

        "inventory": inventory,

        "orders": orders,

        "returns": returns,

        "workers": 2,

        "time": 40

    }


TASK_MAP = {
    "easy": easy_task,
    "medium": medium_task,
    "hard": hard_task
}