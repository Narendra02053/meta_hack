class QLearningAgent:

    def __init__(self):

        self.q_table = {}

        self.alpha = 0.1
        self.gamma = 0.9
        self.epsilon = 0.2

    def choose_action(self, state, actions):

        import random

        state_key = str(state)

        if random.random() < self.epsilon:
            return random.choice(actions)

        if state_key not in self.q_table:
            self.q_table[state_key] = {
                a: 0 for a in actions
            }

        return max(
            self.q_table[state_key],
            key=self.q_table[state_key].get
        )

    def update(self, state, action, reward, next_state):

        state_key = str(state)
        next_state_key = str(next_state)

        old = self.q_table.get(state_key, {}).get(action, 0)
        
        # Ensure state exists in q_table if we are updating it
        if state_key not in self.q_table:
            self.q_table[state_key] = {action: 0}

        future = max(
            self.q_table.get(next_state_key, {}).values(),
            default=0
        )

        new = old + self.alpha * (
            reward
            + self.gamma * future
            - old
        )

        self.q_table[state_key][action] = new

    def save_q_table(self, path="q_table.json"):
        import json
        with open(path, "w") as f:
            json.dump(self.q_table, f)

    def load_q_table(self, path="q_table.json"):
        import json
        try:
            with open(path, "r") as f:
                self.q_table = json.load(f)
        except FileNotFoundError:
            self.q_table = {}
