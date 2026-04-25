import random
from collections import deque


class GridWarehouseEnv:
    """
    Grid-based multi-robot environment used by the Streamlit dashboard.
    (Previously implemented as top-level `warehouse_env.WarehouseEnv`.)
    """

    def __init__(self):
        self.grid_size = (5, 5)
        self.charging_stations = [(0, 0), (4, 4)]
        self.priority_weights = {"HIGH": 4, "NORMAL": 2, "LOW": 1}
        self.obstacles = [(1, 2), (2, 2), (3, 2), (1, 3), (2, 3)]
        self.total_reward = 0
        self.step_count = 0
        self.tasks_completed = 0
        self.rl_actions = [
            "priority_first",
            "nearest_first",
            "deadline_first"
        ]
        self.collisions = 0
        self.successful_tasks_without_conflict = 0
        self.congestion_avoided_count = 0
        self.strategy_usage = {a: 0 for a in self.rl_actions}
        self.emergency_tasks_saved = 0
        self.task_spawn_times = {} 
        self.task_completion_durations = []
        self.episode_history = []
        self.current_strategy = "None"
        self.strategy_reason = "System Idle"
        self.reset()

    def initialize_tasks(self):
        return [
            {
                "id": 0,
                "pickup": (1, 1),
                "drop": (4, 4),
                "priority": "HIGH",
                "deadline": random.randint(15, 30),
                "assigned": None,
                "completed": False,
                "expired": False,
                # Backwards-compatibility: older UI used `failed` to represent expiry.
                "failed": False,
            },
            {
                "id": 1,
                "pickup": (3, 0),
                "drop": (0, 4),
                "priority": "NORMAL",
                "deadline": random.randint(15, 30),
                "assigned": None,
                "completed": False,
                "expired": False,
                "failed": False,
            },
        ]

    def reset(self):
        self.robots = [
            {"id": 0, "position": (0, 0), "battery": 100, "carrying": False, "path": [], "current_target": None},
            {"id": 1, "position": (4, 4), "battery": 100, "carrying": False, "path": [], "current_target": None},
        ]
        self.tasks = self.initialize_tasks()
        # Normalize legacy tasks so the env can safely read both `expired` and `failed`.
        for t in self.tasks:
            if "expired" not in t:
                t["expired"] = bool(t.get("failed", False))
            if "failed" not in t:
                t["failed"] = bool(t.get("expired", False))
        self.logs = ["System reset. Agents initialized."]
        self.event_log: list[str] = []
        self.total_reward = 0
        self.step_count = 0
        self.tasks_completed = 0
        self.collisions = 0
        self.successful_tasks_without_conflict = 0
        self.congestion_avoided_count = 0
        self.strategy_usage = {a: 0 for a in self.rl_actions}
        self.emergency_tasks_saved = 0
        self.task_spawn_times = {t["id"]: 0 for t in self.tasks}
        self.task_completion_durations = []
        self.episode_history = []
        self.current_strategy = "None"
        self.strategy_reason = "System Reset"
        return self.get_state()

    def _log_event(self, message: str):
        self.event_log.append(message)
        if len(self.event_log) > 20:
            self.event_log = self.event_log[-20:]

    def priority_value(self, priority):
        return self.priority_weights.get(priority, 0)

    def get_state(self):
        congestion_zones = []
        robot_positions = [r["position"] for r in self.robots]
        for i in range(len(robot_positions)):
            for j in range(i + 1, len(robot_positions)):
                p1, p2 = robot_positions[i], robot_positions[j]
                if abs(p1[0] - p2[0]) + abs(p1[1] - p2[1]) <= 1:
                    if p1 not in congestion_zones:
                        congestion_zones.append(p1)
                    if p2 not in congestion_zones:
                        congestion_zones.append(p2)

        return {
            "robots": self.robots,
            "tasks": self.tasks,
            "obstacles": self.obstacles,
            "congestion_zones": congestion_zones,
            "logs": self.logs[-5:],
            "event_log": self.event_log[-20:],
            "collisions": self.collisions,
            "coordination_score": round(self.tasks_completed / (self.collisions + 1), 2),
            "strategy_usage": self.strategy_usage,
            "emergency_tasks_saved": self.emergency_tasks_saved,
            "avg_completion_time": round(sum(self.task_completion_durations) / len(self.task_completion_durations), 2) if self.task_completion_durations else 0,
            "tasks_expired": sum(1 for t in self.tasks if t["expired"]),
            "current_strategy": self.current_strategy,
            "strategy_reason": self.strategy_reason,
            "pending_tasks": len([t for t in self.tasks if not t["completed"] and not t["expired"]]),
            "min_deadline": min([t["deadline"] for t in self.tasks if not t["completed"] and not t["expired"]], default=0),
            "highest_priority": max([self.priority_value(t["priority"]) for t in self.tasks if not t["completed"] and not t["expired"]], default=0),
        }

    def get_summary(self):
        perf_rating = 0
        if self.step_count > 0:
            total_tasks = len(self.tasks)
            success_rate = (self.tasks_completed / total_tasks) * 100 if total_tasks > 0 else 0
            efficiency = min(1.0, (self.tasks_completed / self.step_count) * 5)
            perf_rating = int((success_rate * 0.7) + (efficiency * 30))

        return {
            "Total Tasks Completed": self.tasks_completed,
            "Tasks Expired": sum(1 for t in self.tasks if t["expired"]),
            "Emergency Tasks Saved": self.emergency_tasks_saved,
            "Average Completion Time": round(sum(self.task_completion_durations) / len(self.task_completion_durations), 2) if self.task_completion_durations else 0,
            "Coordination Score": round(self.tasks_completed / (self.collisions + 1), 2),
            "Final Efficiency Score": f"{perf_rating}%"
        }

    def get_rl_state(self):
        pending_tasks = len(
            [t for t in self.tasks if not t["completed"] and not t["expired"]]
        )

        highest_priority = max(
            [self.priority_value(t["priority"])
             for t in self.tasks
             if not t["completed"] and not t["expired"]],
            default=0
        )

        min_deadline = min(
            [t["deadline"]
             for t in self.tasks
             if not t["completed"] and not t["expired"]],
            default=0
        )

        return (
            pending_tasks,
            highest_priority,
            min_deadline
        )

    def find_shortest_path(self, start, goal, obstacles, other_robots, grid_size):
        if start == goal:
            return []

        queue = deque([(start, [])])
        visited = {start}

        while queue:
            (cx, cy), path = queue.popleft()

            moves = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            moves.sort(key=lambda m: abs(cx + m[0] - goal[0]) + abs(cy + m[1] - goal[1]))

            for dx, dy in moves:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < grid_size[0] and 0 <= ny < grid_size[1]:
                    if (nx, ny) == goal:
                        return path + [(nx, ny)]
                    if (nx, ny) not in visited and (nx, ny) not in obstacles and (nx, ny) not in other_robots:
                        visited.add((nx, ny))
                        queue.append(((nx, ny), path + [(nx, ny)]))
        return []

    def intelligent_action(self, robot_id, rl_action=None):
        robot = self.robots[robot_id]
        rx, ry = robot["position"]

        target = None
        action_at_target = "wait"

        if robot["battery"] < 25:
            self._log_event(f"Robot {robot['id']} battery low")
            nearest_station = min(self.charging_stations, key=lambda s: abs(s[0] - rx) + abs(s[1] - ry))
            target = nearest_station
            action_at_target = "wait"
        else:
            active_task = next(
                (
                    t
                    for t in self.tasks
                    if t.get("assigned") == robot["id"]
                    and not t.get("completed", False)
                    and not t.get("expired", t.get("failed", False))
                ),
                None,
            )

            if not active_task and not robot["carrying"]:
                # --- Emergency Recovery Logic ---
                critical_tasks = [
                    t for t in self.tasks
                    if not t["completed"] and not t["expired"] and t["deadline"] <= 2
                    and t["assigned"] is None
                ]
                
                if critical_tasks:
                    best_task = min(critical_tasks, key=lambda t: t["deadline"])
                    
                    if self.current_strategy != "emergency_override":
                        self.current_strategy = "emergency_override"
                        self.strategy_reason = f"Critical Task {best_task['id']} (Deadline: {best_task['deadline']})"
                        self.logs.append(f"Strategy switched to emergency_override")

                    best_task["assigned"] = robot["id"]
                    best_task["critical"] = True
                    active_task = best_task
                    self.logs.append(f"Emergency Mode Activated for Task {best_task['id']}")
                    self._log_event(f"EMERGENCY: Robot {robot['id']} taking Task {best_task['id']}")
                else:
                    available_tasks = [
                        t
                        for t in self.tasks
                        if t.get("assigned") is None
                        and not t.get("completed", False)
                        and not t.get("expired", t.get("failed", False))
                    ]
                    if available_tasks:
                        if rl_action in self.rl_actions:
                            self.strategy_usage[rl_action] += 1
                            if self.current_strategy != rl_action:
                                self.current_strategy = rl_action
                                self.strategy_reason = "RL Agent optimized selection"
                                self.logs.append(f"Strategy switched to {rl_action}")
                        
                        if rl_action == "priority_first":
                            best_task = max(available_tasks, key=lambda t: self.priority_value(t["priority"]))
                        elif rl_action == "nearest_first":
                            best_task = min(available_tasks, key=lambda t: abs(rx - t["pickup"][0]) + abs(ry - t["pickup"][1]))
                        elif rl_action == "deadline_first":
                            best_task = min(available_tasks, key=lambda t: t["deadline"])
                        else:
                            # Fallback to existing logic
                            if self.current_strategy != "urgency_heuristic":
                                self.current_strategy = "urgency_heuristic"
                                self.strategy_reason = "Standard operational logic"
                                self.logs.append("Strategy switched to urgency_heuristic")
                            
                            max_deadline = 30
                            priority_score_map = {"HIGH": 50, "NORMAL": 30, "LOW": 10}

                            def urgency_score(task):
                                tx, ty = task["pickup"]
                                distance_penalty = abs(rx - tx) + abs(ry - ty)
                                priority_score = priority_score_map.get(task.get("priority", "NORMAL"), 30)
                                current_deadline = int(task.get("deadline", max_deadline))
                                deadline_score = max_deadline - current_deadline
                                return priority_score + deadline_score - distance_penalty

                            best_task = max(available_tasks, key=urgency_score)

                        best_task["assigned"] = robot["id"]
                        active_task = best_task
                        self.logs.append(f"Agent {robot['id']+1} assigned {best_task['priority']} Task #{best_task['id']} using {rl_action or 'urgency_score'}.")
                        self._log_event(f"Robot {robot['id']} assigned Task {best_task['id']}")

            if active_task:
                if robot["carrying"]:
                    target = active_task["drop"]
                    action_at_target = "drop"
                else:
                    target = active_task["pickup"]
                    action_at_target = "pickup"
            else:
                return "wait"

        if target:
            if (rx, ry) == target:
                robot["path"] = []
                robot["current_target"] = None
                return action_at_target

            other_robots = [r["position"] for r in self.robots if r["id"] != robot_id]

            recalculate = False
            if robot["current_target"] != target or not robot["path"]:
                recalculate = True
            else:
                next_step = robot["path"][0]
                if next_step in self.obstacles or next_step in other_robots:
                    recalculate = True

            if recalculate:
                robot["current_target"] = target
                path = self.find_shortest_path((rx, ry), target, self.obstacles, other_robots, self.grid_size)
                if not path:
                    path = self.find_shortest_path((rx, ry), target, self.obstacles, [], self.grid_size)
                    if path and path[0] in other_robots:
                        path = []
                robot["path"] = path

            if robot["path"]:
                nx, ny = robot["path"].pop(0)
                if nx < rx:
                    return "move_up"
                if nx > rx:
                    return "move_down"
                if ny < ry:
                    return "move_left"
                if ny > ry:
                    return "move_right"

            return "wait"

        return "wait"

    def step(self, robot_id, action):
        robot = self.robots[robot_id]
        reward = 0
        done = False

        for task in self.tasks:
            expired = task.get("expired", task.get("failed", False))
            if not task.get("completed", False) and not expired:
                task["deadline"] = int(task.get("deadline", 0)) - 1
                if task["deadline"] <= 0:
                    task["expired"] = True
                    task["failed"] = True  # compatibility
                    reward -= 20
                    self.logs.append(f"Task #{task['id']} expired (deadline reached).")
                    self._log_event(f"Robot {robot_id} task expired Task {task['id']}")
                    self._log_event(f"Task {task['id']} expired")
                    # Safety: if a robot was carrying for an expired task, drop the carry flag.
                    if task.get("assigned") is not None:
                        self.robots[task["assigned"]]["carrying"] = False

        active_task = next(
            (
                t
                for t in self.tasks
                if t.get("assigned") == robot["id"]
                and not t.get("completed", False)
                and not t.get("expired", t.get("failed", False))
            ),
            None,
        )

        robot_positions = [r["position"] for r in self.robots]
        rx, ry = robot["position"]
        is_congested = any(abs(rx - rp[0]) + abs(ry - rp[1]) <= 1 for idx, rp in enumerate(robot_positions) if idx != robot_id)

        if is_congested and action in ["move_up", "move_down", "move_left", "move_right"] and random.random() < 0.3:
            action = "wait"
            reward -= 1
            self.congestion_avoided_count += 1
            self.logs.append(f"Agent {robot['id']+1} navigating tight corridor.")

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

                if (nx, ny) in self.obstacles:
                    robot["position"] = previous_position
                    reward -= 10
                    self.logs.append(f"Agent {robot['id']+1} hit obstacle at {(nx, ny)}!")
                elif nx < 0 or nx >= self.grid_size[0] or ny < 0 or ny >= self.grid_size[1]:
                    robot["position"] = previous_position
                    reward -= 5
                else:
                    new_robot_positions = [r["position"] for r in self.robots]
                    if len(new_robot_positions) != len(set(new_robot_positions)):
                        robot["position"] = previous_position
                        reward -= 20
                        self.collisions += 1
                        self._log_event(f"Robot {robot['id']} collision avoided")

                    if any(abs(nx - rp[0]) + abs(ny - rp[1]) <= 1 for idx, rp in enumerate(new_robot_positions) if idx != robot_id):
                        reward -= 1

                if robot["battery"] <= 0:
                    reward -= 10
                    self.logs.append(f"Agent {robot['id']+1} battery depleted!")

        elif action == "pickup":
            if active_task and not robot["carrying"] and robot["position"] == active_task["pickup"]:
                robot["carrying"] = True
                reward += 20
                self.logs.append(f"Agent {robot['id']+1} picked up Task #{active_task['id']}.")
                self._log_event(f"Robot {robot['id']} picked Task {active_task['id']}")

        elif action == "drop":
            if active_task and robot["carrying"] and robot["position"] == active_task["drop"]:
                robot["carrying"] = False
                active_task["completed"] = True
                reward += 70

                if active_task.get("critical"):
                    reward += 10
                    self.emergency_tasks_saved += 1
                    self.logs.append(f"Critical Task #{active_task['id']} SAVED! +10 Bonus.")

                # Track completion time
                spawn_time = self.task_spawn_times.get(active_task["id"], 0)
                self.task_completion_durations.append(self.step_count - spawn_time)

                if active_task["priority"] == "HIGH":
                    reward += 10
                elif active_task["priority"] == "LOW":
                    reward += 2

                self.tasks_completed += 1
                self.logs.append(f"Agent {robot['id']+1} completed Task #{active_task['id']}.")
                self._log_event(f"Robot {robot['id']} delivered Task {active_task['id']}")

        if robot["position"] in self.charging_stations and robot["battery"] < 100:
            robot["battery"] = 100
            reward += 10
            self.logs.append(f"Agent {robot['id']+1} recharged battery.")
            self._log_event(f"Robot {robot['id']} recharging")

        self.step_count += 1
        self.total_reward += reward

        if all(task["completed"] or task["failed"] for task in self.tasks):
            reward += 150
            self.total_reward += 150
            done = True
            self.logs.append("Simulation sequence finished.")

        # Record history for replay
        self.episode_history.append({
            "step": self.step_count,
            "robot_id": robot_id,
            "action": action,
            "state": self.get_state()
        })

        return self.get_state(), reward, done

    def add_random_task(self):
        new_id = len(self.tasks)

        def get_valid_pos():
            while True:
                pos = (random.randint(0, 4), random.randint(0, 4))
                if pos not in self.obstacles:
                    return pos

        pickup = get_valid_pos()
        drop = get_valid_pos()
        while drop == pickup:
            drop = get_valid_pos()

        self.tasks.append(
            {
                "id": new_id,
                "pickup": pickup,
                "drop": drop,
                "priority": random.choice(["HIGH", "NORMAL", "LOW"]),
                "deadline": random.randint(15, 30),
                "assigned": None,
                "completed": False,
                "expired": False,
                "failed": False,
            }
        )
        self.task_spawn_times[new_id] = self.step_count
        self.logs.append(f"New task #{new_id} spawned at {pickup}.")
        return self.get_state()
