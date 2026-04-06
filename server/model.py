import random

class SmartAgent:
    def __init__(self, actions=None):
        pass

    def act(self, state):
        inventory = state.get("inventory", {})
        order = state.get("current_order")
        inspections = state.get("inspection_pending", [])
        returns = state.get("returns_pending", [])
        packed = state.get("packed_orders", 0)
        shipped = state.get("shipped_orders", 0)

        # 1. Ship any packed orders
        if packed > shipped:
            return "ship_order"

        # 2. Restock items to boost inventory
        if inspections:
            return f"restock_{inspections[0]}"

        # 3. Handle Order Picking
        if order:
            # Check if we have all items
            all_picked = True
            for product, count in order.items():
                if count > 0:
                    all_picked = False
                    # Can we pick this item?
                    if inventory.get(product, 0) > 0:
                        return f"pick_{product}"
            
            if all_picked:
                return "pack_order"

        # 4. Process Returns if inventory is low or order can't be fulfilled
        if returns:
            return "inspect_return"

        # 5. Fallback to wait (minimal penalty)
        return "wait"
