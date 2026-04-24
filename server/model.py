import random

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

        # 1. Ship any packed orders immediately to advance current_order_index
        if packed > shipped:
            return "ship_order"

        # 2. Handle Order Processing (Primary Goal for Time Efficiency)
        if order:
            all_picked = True
            needed_item = None
            for product, count in order.items():
                if count > 0:
                    all_picked = False
                    # Can we pick this item?
                    if inventory.get(product, 0) > 0:
                        return f"pick_{product}"
                    else:
                        needed_item = product
                        break # Stop looking, we found a bottleneck
            
            if all_picked:
                return "pack_order"

            # 3. Only if bottlenecked by stock, try to find the item in inspections/returns
            if needed_item:
                # Is it in the inspection queue?
                if needed_item in inspections:
                    return f"restock_{needed_item}"
                
                # Is it in the returns queue?
                if needed_item in returns:
                    return "inspect_return"

        # 4. If not bottlenecked but have extra time/no order, handle other tasks
        # But wait - every action costs time. To get 0.90+, we MUST minimize actions.
        # So we skip "nice-to-have" restocking unless we are literally waiting.
        
        if order is None:
            # All orders potentially done or at the very end
            if returns: return "inspect_return"
            if inspections: return f"restock_{inspections[0]}"

        # 5. Fallback to wait (minimal penalty, but costs 1 time step)
        return "wait"
