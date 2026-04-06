import random

class RandomAgent:
    def __init__(self, actions):
        self.actions = actions

    def act(self, state):
        # A simple heuristic: if there's a return, maybe inspect it.
        # If there's an inspection pending, restock.
        # Otherwise pick or ship.
        
        if state.get("inspection_pending") and len(state["inspection_pending"]) > 0:
            return f"restock_{state['inspection_pending'][0]}"
            
        if state.get("returns_pending") and len(state["returns_pending"]) > 0:
            return "inspect_return"
            
        if state.get("current_order"):
            # Sample from possible actions
            return random.choice(self.actions)
            
        return "wait"
