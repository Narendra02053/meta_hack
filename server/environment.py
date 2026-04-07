import copy
import random
from server.schema import Observation


class WarehouseEnv:

    def __init__(self, task_config):

        self.initial_inventory = task_config["inventory"]

        self.initial_orders = task_config["orders"]

        self.initial_returns = task_config.get(
            "returns", []
        )

        self.workers_available = task_config["workers"]

        self.time_limit = task_config["time"]

        self.reset()


    def reset(self):

        self.inventory = copy.deepcopy(
            self.initial_inventory
        )

        self.orders = copy.deepcopy(
            self.initial_orders
        )

        self.returns_queue = copy.deepcopy(
            self.initial_returns
        )

        self.inspection_queue = []

        self.current_order_index = 0

        self.packed_orders = 0

        self.shipped_orders = 0

        self.time_left = self.time_limit


        # ⏱️ Deadlines per order
        self.order_deadlines = [

            random.randint(8, 15)

            for _ in self.orders

        ]

        return self.get_state()


    def get_state(self) -> Observation:

        current_order = None

        deadline = None

        priority = "Normal"


        if self.current_order_index < len(self.orders):

            current_order = self.orders[
                self.current_order_index
            ]

            deadline = self.order_deadlines[
                self.current_order_index
            ]

            # 🔴 Priority Escalation
            if deadline is not None and deadline <= 3:

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
            time_limit=self.time_limit
        )


    def step(self, action):

        reward = 0

        done = False

        info = {}


        # --------------------
        # Deadline Countdown
        # --------------------

        if self.current_order_index < len(self.order_deadlines):

            self.order_deadlines[
                self.current_order_index
            ] -= 1


        # --------------------
        # Handle Returns
        # --------------------

        if action == "inspect_return":

            if len(self.returns_queue) > 0:

                returned_item = \
                    self.returns_queue.pop(0)

                self.inspection_queue.append(
                    returned_item
                )

                reward += 0.2

            else:

                reward -= 0.2


        # --------------------
        # Restock Items
        # --------------------

        elif action.startswith("restock_"):

            product = action.split("_")[1]

            if product in self.inspection_queue:

                self.inspection_queue.remove(
                    product
                )

                self.inventory[product] += 1

                reward += 0.3

            else:

                reward -= 0.2


        # --------------------
        # Order Processing
        # --------------------

        elif self.current_order_index < len(self.orders):

            current_order = self.orders[
                self.current_order_index
            ]


            # PICK ITEM

            if action.startswith("pick_"):

                product = action.split("_")[1]

                if (
                    product in current_order
                    and self.inventory.get(
                        product, 0
                    ) > 0
                    and current_order[product] > 0
                ):

                    self.inventory[product] -= 1

                    current_order[product] -= 1

                    reward += 0.2

                else:

                    reward -= 0.3


            # PACK ORDER

            elif action == "pack_order":

                if all(
                    v == 0
                    for v in current_order.values()
                ):

                    self.packed_orders += 1

                    reward += 0.3

                else:

                    reward -= 0.3


            # SHIP ORDER (with Priority Logic)

            elif action == "ship_order":

                if (
                    self.packed_orders
                    > self.shipped_orders
                ):

                    deadline = self.order_deadlines[
                        self.current_order_index
                    ]


                    # 🔴 Priority-Based Reward

                    if deadline >= 0:

                        if deadline <= 3:

                            # Urgent success
                            reward += 1.0

                        else:

                            # Normal success
                            reward += 0.5

                    else:

                        if deadline <= 3:

                            # Late urgent penalty
                            reward -= 1.0

                        else:

                            reward -= 0.5


                    self.shipped_orders += 1

                    self.current_order_index += 1

                else:

                    reward -= 0.3


        # WAIT

        elif action == "wait":

            reward -= 0.1


        # --------------------
        # Time Reduction
        # --------------------

        self.time_left -= 1


        if self.time_left <= 0:

            done = True


        # --------------------
        # Completion Bonus
        # --------------------

        if self.current_order_index >= len(self.orders):

            reward += 1.0

            done = True


        return self.get_state(), reward, done, info