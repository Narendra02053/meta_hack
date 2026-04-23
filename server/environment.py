import copy
import random
from server.schema import Observation


class WarehouseEnv:

    def __init__(self, task_config):
        self.initial_inventory = task_config["inventory"]
        self.initial_orders = task_config["orders"]
        self.initial_returns = task_config.get("returns", [])
        self.workers_available = task_config["workers"]
        self.time_limit = task_config["time"]
        self.reset()


    def reset(self):
        self.inventory = copy.deepcopy(self.initial_inventory)
        self.orders = copy.deepcopy(self.initial_orders)
        self.returns_queue = copy.deepcopy(self.initial_returns)
        self.inspection_queue = []
        self.current_order_index = 0
        self.packed_orders = 0
        self.shipped_orders = 0
        self.time_left = self.time_limit

        # Deadlines per order
        self.order_deadlines = [random.randint(8, 15) for _ in self.orders]

        # Random Urgent Events
        self.random_urgent_flags = [random.random() < 0.1 for _ in self.orders]

        # Performance Metrics
        self.metrics = {
            "orders_completed": 0,
            "urgent_orders_completed": 0,
            "late_orders": 0,
            "stockouts": 0,
            "restocks_triggered": 0,
            "total_steps": 0,
        }

        return self.get_state()


    def get_state(self) -> Observation:
        current_order = None
        deadline = None
        priority = "Normal"

        if self.current_order_index < len(self.orders):
            current_order = self.orders[self.current_order_index]
            deadline = self.order_deadlines[self.current_order_index]

            # Priority Escalation
            if deadline is not None and deadline <= 3:
                priority = "Urgent"
            # Random Urgent Event
            elif self.random_urgent_flags[self.current_order_index]:
                priority = "Urgent"

        return Observation(
            inventory=self.inventory,
            current_order=current_order,
            current_deadline=deadline,
            priority=priority,
            returns_pending=self.returns_queue,
            inspection_pending=self.inspection_queue,
            packed_orders=self.packed_orders,
            shipped_orders=self.shipped_orders,
            time_left=self.time_left,
            total_orders=len(self.orders),
            time_limit=self.time_limit,
        )


    def print_state_summary(self):
        """Prints a readable snapshot of the warehouse status."""
        print("\n" + "=" * 30)
        print("      [WAREHOUSE SUMMARY]      ")
        print("=" * 30)
        print(f"Total Orders         : {len(self.orders)}")
        print(f"Orders Completed     : {self.metrics['orders_completed']}")
        print(f"Urgent Orders Handled: {self.metrics['urgent_orders_completed']}")
        print(f"Late Orders          : {self.metrics['late_orders']}")
        print(f"Stockouts            : {self.metrics['stockouts']}")
        print(f"Restocks Triggered   : {self.metrics['restocks_triggered']}")
        print(f"Total Steps Used     : {self.metrics['total_steps']}/{self.time_limit}")
        print(f"Remaining Time Steps : {self.time_left}")
        print("=" * 30 + "\n")


    def step(self, action):
        reward = 0
        done = False
        info = {}

        self.metrics["total_steps"] += 1

        # Random External Event
        if random.random() < 0.1:
            reward -= 0.1
            info["message"] = "External delay occurred"

        # Deadline Countdown
        if self.current_order_index < len(self.order_deadlines):
            self.order_deadlines[self.current_order_index] -= 1
            if self.order_deadlines[self.current_order_index] == 0:
                reward -= 0.5
                info["message"] = "Order status: late"
                self.metrics["late_orders"] += 1

        # Handle Returns
        if action == "inspect_return":
            if len(self.returns_queue) > 0:
                returned_item = self.returns_queue.pop(0)
                self.inspection_queue.append(returned_item)
                reward += 0.2
            else:
                reward -= 0.2

        # Restock Items
        elif action.startswith("restock_"):
            product = action.split("_")[1]
            if product in self.inspection_queue:
                self.inspection_queue.remove(product)
                self.inventory[product] += 1
                reward += 0.3
            else:
                reward -= 0.2

        # Order Processing
        elif self.current_order_index < len(self.orders):
            current_order = self.orders[self.current_order_index]

            # Pick Item
            if action.startswith("pick_"):
                product = action.split("_")[1]
                if self.inventory.get(product, 0) <= 0:
                    reward -= 0.3
                    info["message"] = f"Out of stock for {product}"
                    self.metrics["stockouts"] += 1
                elif product in current_order and self.inventory.get(product, 0) > 0 and current_order[product] > 0:
                    self.inventory[product] -= 1
                    current_order[product] -= 1
                    reward += 0.2
                else:
                    reward -= 0.3

            # Pack Order
            elif action == "pack_order":
                if all(v == 0 for v in current_order.values()):
                    self.packed_orders += 1
                    reward += 0.3
                else:
                    reward -= 0.3

            # Ship Order (with Priority Logic)
            elif action == "ship_order":
                if self.packed_orders > self.shipped_orders:
                    deadline = self.order_deadlines[self.current_order_index]

                    # Priority-Based Reward
                    if deadline >= 0:
                        if deadline <= 3:
                            reward += 1.0  # Urgent success
                        else:
                            reward += 0.5  # Normal success
                    else:
                        if deadline <= 3:
                            reward -= 1.0  # Late urgent penalty
                        else:
                            reward -= 0.5

                    # Priority-Based Reward Boost
                    is_urgent = (deadline <= 3) or self.random_urgent_flags[self.current_order_index]
                    if is_urgent:
                        if deadline >= 0:
                            reward += 0.3  # bonus for urgent success
                        else:
                            reward -= 0.3  # extra penalty for urgent failure

                    self.metrics["orders_completed"] += 1
                    if is_urgent:
                        self.metrics["urgent_orders_completed"] += 1

                    self.shipped_orders += 1
                    self.current_order_index += 1
                else:
                    reward -= 0.3

        # Wait
        elif action == "wait":
            reward -= 0.1

        # Time Reduction
        self.time_left -= 1
        if self.time_left <= 0:
            done = True

        # Completion Bonus
        if self.current_order_index >= len(self.orders):
            reward += 1.0
            done = True

        # Auto-Restocking Strategy
        for product, count in self.inventory.items():
            if count < 2:
                self.inventory[product] += 5
                reward -= 0.05
                info["message"] = f"Auto-restocked {product} due to low inventory"
                self.metrics["restocks_triggered"] += 1

        # Print Metrics Summary when finished
        if done:
            self.print_state_summary()

        return self.get_state(), reward, done, info