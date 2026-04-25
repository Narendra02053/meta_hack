import random


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
    "router",
]


def generate_inventory(size: int, min_stock: int = 20, max_stock: int = 50) -> dict[str, int]:
    inventory: dict[str, int] = {}
    selected = random.sample(PRODUCTS, size)
    for product in selected:
        inventory[product] = random.randint(min_stock, max_stock)
    return inventory


def generate_orders(
    inventory: dict[str, int], num_orders: int, min_items: int = 1, max_items: int = 2
) -> list[dict[str, int]]:
    orders: list[dict[str, int]] = []
    products = list(inventory.keys())
    for _ in range(num_orders):
        order: dict[str, int] = {}
        num_items = random.randint(min_items, max_items)
        selected = random.sample(products, num_items)
        for p in selected:
            order[p] = 1
        orders.append(order)
    return orders


def generate_returns(inventory: dict[str, int], num_returns: int) -> list[str]:
    products = list(inventory.keys())
    return random.sample(products, num_returns)


def easy_task() -> dict:
    inventory = generate_inventory(5)
    orders = generate_orders(inventory, 3)
    returns = generate_returns(inventory, 1)
    return {"inventory": inventory, "orders": orders, "returns": returns, "workers": 1, "time": 100}


def medium_task() -> dict:
    inventory = generate_inventory(8)
    orders = generate_orders(inventory, 6)
    returns = generate_returns(inventory, 2)
    return {"inventory": inventory, "orders": orders, "returns": returns, "workers": 2, "time": 200}


def hard_task() -> dict:
    inventory = generate_inventory(10, min_stock=30, max_stock=60)
    orders = generate_orders(inventory, 15, min_items=1, max_items=2)
    returns = generate_returns(inventory, 4)
    return {"inventory": inventory, "orders": orders, "returns": returns, "workers": 2, "time": 500}


TASK_MAP = {"easy": easy_task, "medium": medium_task, "hard": hard_task}

