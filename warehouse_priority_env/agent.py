class SmartAgent:
    def __init__(self, actions=None):
        pass

    def act(self, state):
        # Support both Pydantic model (Observation) and regular dictionary
        if hasattr(state, "model_dump"):
            s = state.model_dump()
        else:
            s = state

        inventory = s.get("inventory", {})
        order = s.get("current_order")
        inspections = s.get("inspection_pending", [])
        returns = s.get("returns_pending", [])
        packed = s.get("packed_orders", 0)
        shipped = s.get("shipped_orders", 0)

        if packed > shipped:
            return "ship_order"

        if order:
            all_picked = True
            needed_item = None
            for product, count in order.items():
                if count > 0:
                    all_picked = False
                    if inventory.get(product, 0) > 0:
                        return f"pick_{product}"
                    needed_item = product
                    break

            if all_picked:
                return "pack_order"

            if needed_item:
                if needed_item in inspections:
                    return f"restock_{needed_item}"
                if needed_item in returns:
                    return "inspect_return"

        if order is None:
            if returns:
                return "inspect_return"
            if inspections:
                return f"restock_{inspections[0]}"

        return "wait"

