import random

class WarehouseEnv:
    def __init__(self):
        # Define grid size to manage wall collisions (5x5 grid)
        self.grid_size = (5, 5)
        # 1. Add Recharge Station locations
        self.charging_stations = [(0, 0), (4, 4)]
        self.priority_weights = {
            "HIGH": 3,
            "NORMAL": 2,
            "LOW": 1
        }
        self.total_reward = 0
        self.step_count = 0
        self.tasks_completed = 0
        self.reset()

    def initialize_tasks(self):
        # Initial task queue setup
        return [
            {
                "id": 0,
                "pickup": (1, 1),
                "drop": (4, 4),
                "priority": random.choice(["HIGH", "NORMAL", "LOW"]),
                "assigned": None,
                "completed": False
            },
            {
                "id": 1,
                "pickup": (3, 0),
                "drop": (0, 4),
                "priority": random.choice(["HIGH", "NORMAL", "LOW"]),
                "assigned": None,
                "completed": False
            }
        ]

    def reset(self):
        self.robots = [
            {"id": 0, "position": (0, 0), "battery": 100, "carrying": False},
            {"id": 1, "position": (4, 4), "battery": 100, "carrying": False}
        ]

        self.tasks = self.initialize_tasks()
        self.logs = ["System reset. Agents initialized."]
        self.total_reward = 0
        self.step_count = 0
        self.tasks_completed = 0

        return self.get_state()

    def get_state(self):
        state = {
            "robots": self.robots,
            "tasks": self.tasks,
            "logs": self.logs[-5:] # Return last 5 logs
        }
        return state

    def sample_action(self, robot_id):
        actions = ["move_up", "move_down", "move_left", "move_right", "pickup", "drop", "wait"]
        return random.choice(actions)

    def intelligent_action(self, robot_id):
        robot = self.robots[robot_id]
        rx, ry = robot["position"]
        
        target = None
        action_at_target = "wait"

        # 3. If battery low (<20), move to nearest charging station
        if robot["battery"] < 20:
            nearest_station = min(self.charging_stations, key=lambda s: abs(s[0] - rx) + abs(s[1] - ry))
            target = nearest_station
            action_at_target = "wait"
        else:
            # STEP 3 — Implement Intelligent Task Selection
            # Check for active task already assigned to this robot
            active_task = next((t for t in self.tasks if t["assigned"] == robot["id"] and not t["completed"]), None)
            
            if not active_task and not robot["carrying"]:
                # Try to pick a new task
                available_tasks = [t for t in self.tasks if t["assigned"] is None and not t["completed"]]
                
                if available_tasks:
                    def distance(task):
                        tx, ty = task["pickup"]
                        return abs(rx - tx) + abs(ry - ty)
                    
                    # Sort by priority (descending) and distance (ascending)
                    available_tasks.sort(key=lambda t: (-self.priority_weights[t["priority"]], distance(t)))
                    
                    # Assign best task
                    best_task = available_tasks[0]
                    best_task["assigned"] = robot["id"]
                    active_task = best_task
                    self.logs.append(f"Agent {robot['id']+1} auto-assigned {best_task['priority']} Task #{best_task['id']}.")

            if active_task:
                # 2. If robot carrying, move toward drop location
                if robot["carrying"]:
                    target = active_task["drop"]
                    action_at_target = "drop"
                # 1. If robot not carrying, move toward pickup location
                else:
                    target = active_task["pickup"]
                    action_at_target = "pickup"
            else:
                return "wait"

        # 4. Movement Strategy (with basic avoidance)
        if target:
            tx, ty = target
            
            # Perform action if already at target
            if rx == tx and ry == ty:
                return action_at_target
                
            preferred_moves = []
            if rx < tx: preferred_moves.append("move_down")
            if rx > tx: preferred_moves.append("move_up")
            if ry < ty: preferred_moves.append("move_right")
            if ry > ty: preferred_moves.append("move_left")
            
            # Check for robot-to-robot collision for preferred moves
            robot_positions = [r["position"] for r in self.robots if r["id"] != robot_id]
            
            for move in preferred_moves:
                nx, ny = rx, ry
                if move == "move_down": nx += 1
                elif move == "move_up": nx -= 1
                elif move == "move_right": ny += 1
                elif move == "move_left": ny -= 1
                
                if (nx, ny) not in robot_positions:
                    return move
            
            # If all preferred moves blocked, wait to avoid gridlock
            return "wait"

        return "wait"

    def step(self, robot_id, action):
        robot = self.robots[robot_id]
        reward = 0
        done = False

        # Get the task assigned to this robot
        active_task = next((t for t in self.tasks if t["assigned"] == robot["id"] and not t["completed"]), None)

        # 2. Movement Logic & Collision Detection
        if action in ["move_up", "move_down", "move_left", "move_right"]:
            if robot["battery"] <= 0:
                reward -= 10
            else:
                x, y = robot["position"]
                previous_position = (x, y)
                
                if action == "move_up":
                    robot["position"] = (x - 1, y)
                elif action == "move_down":
                    robot["position"] = (x + 1, y)
                elif action == "move_left":
                    robot["position"] = (x, y - 1)
                elif action == "move_right":
                    robot["position"] = (x, y + 1)

                robot["battery"] -= 1
                reward -= 1

                nx, ny = robot["position"]
                if nx < 0 or nx >= self.grid_size[0] or ny < 0 or ny >= self.grid_size[1]:
                    robot["position"] = previous_position
                    reward -= 5
                else:
                    robot_positions = [r["position"] for r in self.robots]
                    if len(robot_positions) != len(set(robot_positions)):
                        robot["position"] = previous_position
                        reward -= 20

                if robot["battery"] <= 0:
                    reward -= 10
                    self.logs.append(f"Agent {robot['id']+1} battery depleted!")

        elif action == "pickup":
            if active_task and not robot["carrying"]:
                if robot["position"] == active_task["pickup"]:
                    robot["carrying"] = True
                    reward += 10
                    self.logs.append(f"Agent {robot['id']+1} picked up Task #{active_task['id']}.")

        elif action == "drop":
            if active_task and robot["carrying"]:
                if robot["position"] == active_task["drop"]:
                    robot["carrying"] = False
                    active_task["completed"] = True
                    reward += 50
                    
                    # STEP 6 — Add Priority Reward Bonus
                    if active_task["priority"] == "HIGH":
                        reward += 5
                    elif active_task["priority"] == "LOW":
                        reward += 1
                        
                    self.tasks_completed += 1
                    self.logs.append(f"Agent {robot['id']+1} completed {active_task['priority']} Task #{active_task['id']}.")

        if robot["position"] in self.charging_stations:
            if robot["battery"] < 100:
                robot["battery"] = 100
                reward += 5
                self.logs.append(f"Agent {robot['id']+1} recharged battery.")

        self.step_count += 1
        self.total_reward += reward

        if all(task["completed"] for task in self.tasks):
            reward += 100
            self.total_reward += 100
            done = True
            self.logs.append("All warehouse tasks fulfilled!")

        return self.get_state(), reward, done

    def add_random_task(self):
        new_id = len(self.tasks)
        pickup = (random.randint(0, self.grid_size[0]-1), random.randint(0, self.grid_size[1]-1))
        drop = (random.randint(0, self.grid_size[0]-1), random.randint(0, self.grid_size[1]-1))
        
        # Ensure pickup and drop are not the same
        while drop == pickup:
            drop = (random.randint(0, self.grid_size[0]-1), random.randint(0, self.grid_size[1]-1))

        self.tasks.append({
            "id": new_id,
            "pickup": pickup,
            "drop": drop,
            "priority": random.choice(["HIGH", "NORMAL", "LOW"]),
            "assigned": None,
            "completed": False
        })
        self.logs.append(f"New dynamic task #{new_id} spawned at {pickup}.")
        return self.get_state()

if __name__ == "__main__":
    env = WarehouseEnv()
    print("Initial State:", env.get_state())
