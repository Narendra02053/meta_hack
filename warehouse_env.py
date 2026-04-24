import random

class WarehouseEnv:
    def __init__(self):
        # Define grid size to manage wall collisions (5x5 grid)
        self.grid_size = (5, 5)
        # 1. Add Recharge Station locations
        self.charging_stations = [(0, 0), (4, 4)]
        self.reset()

    def initialize_tasks(self):
        # Initial task queue setup
        return [
            {
                "id": 0,
                "pickup": (1, 1),
                "drop": (4, 4),
                "assigned": None,
                "completed": False
            },
            {
                "id": 1,
                "pickup": (3, 0),
                "drop": (0, 4),
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
            # Check for active task
            active_task = next((t for t in self.tasks if t["assigned"] == robot["id"] and not t["completed"]), None)
            
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

        # 1. Dynamic Task Assignment
        active_task = next((t for t in self.tasks if t["assigned"] == robot["id"] and not t["completed"]), None)
        
        if active_task is None and not robot["carrying"]:
            available_task = next((t for t in self.tasks if t["assigned"] is None and not t["completed"]), None)
            if available_task:
                available_task["assigned"] = robot["id"]
                active_task = available_task
                self.logs.append(f"Agent {robot['id']+1} assigned Task #{available_task['id']}.")

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
                    self.logs.append(f"Agent {robot['id']+1} completed Task #{active_task['id']}.")

        if robot["position"] in self.charging_stations:
            if robot["battery"] < 100:
                robot["battery"] = 100
                reward += 5
                self.logs.append(f"Agent {robot['id']+1} recharged battery.")

        completed_tasks = sum(1 for t in self.tasks if t["completed"])
        if completed_tasks == len(self.tasks):
            done = True
            reward += 100
            self.logs.append("All warehouse tasks fulfilled!")

        return self.get_state(), reward, done

if __name__ == "__main__":
    env = WarehouseEnv()
    
    print("Initial State:", env.get_state())
    
    # 1. Drain battery to test movement prevention and recharge at station
    env.robots[0]["battery"] = 1
    print("\nSetting Robot 0 battery to 1...")
    
    # Move should work, battery goes to 0
    state, reward, done = env.step(robot_id=0, action="move_down")
    print(f"After Robot 0 move_down | Battery: {state['robots'][0]['battery']} | Position: {state['robots'][0]['position']} | Reward: {reward}")
    
    # Move should fail because battery is 0
    state, reward, done = env.step(robot_id=0, action="move_down")
    print(f"After Robot 0 dead move attempt | Battery: {state['robots'][0]['battery']} | Position: {state['robots'][0]['position']} | Reward: {reward}")

    # Manually place dead robot on charging station and test recharge
    env.robots[0]["position"] = (0, 0)
    # Simulate a wait/pickup step to trigger recharge at the station
    state, reward, done = env.step(robot_id=0, action="wait")
    print(f"After Robot 0 placed on station (0,0) | Battery: {state['robots'][0]['battery']} | Position: {state['robots'][0]['position']} | Reward: {reward}")
