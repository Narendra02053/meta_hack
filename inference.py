import os
import httpx
import time

API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://localhost:7860"  # Default Docker port for HF Spaces
)


def run():
    print(f"📡 Connecting to: {API_BASE_URL}")
    
    try:
        # 1. Reset Environment
        print("\n[INIT] Resetting Environment...")
        response = httpx.post(f"{API_BASE_URL}/reset", params={"difficulty": "easy"})
        if response.status_code != 200:
            print(f"❌ Error Resetting: {response.text}")
            return
            
        data = response.json()
        state = data["state"]
        
        done = False
        step_count = 0
        total_reward = 0

        # 2. Main Agent Loop
        print("[AGENT] Starting Warehouse Optimization Routine...")
        while not done and step_count < 500:
            step_count += 1
            action = "wait" # Default action

            
            # --- AGENT LOGIC ---
            order = state.get("current_order")
            inventory = state.get("inventory", {})
            inspections = state.get("inspection_pending", [])
            returns = state.get("returns_pending", [])
            packed = state.get("packed_orders", 0)
            shipped = state.get("shipped_orders", 0)

            # Prioritize Shipping if packed
            if packed > shipped:
                action = "ship_order"
            
            # Resolve Inspections to refill inventory
            elif inspections:
                action = f"restock_{inspections[0]}"
            
            # Pick items for the current order
            elif order:
                # Find an item that is still needed (value > 0) and available in inventory
                target_product = None
                for product, needed_count in order.items():
                    if needed_count > 0:
                        if inventory.get(product, 0) > 0:
                            target_product = product
                            break
                
                if target_product:
                    action = f"pick_{target_product}"
                elif all(v == 0 for v in order.values()):
                    # All items picked, time to pack
                    action = "pack_order"
                else:
                    # Missing inventory for required items, check returns
                    if returns:
                        action = "inspect_return"
            
            # If everything else fails, try to inspect a return
            elif returns:
                action = "inspect_return"

            # Execute Step
            print(f"[Step {step_count}] Action: {action.ljust(15)}", end=" | ")
            step_resp = httpx.post(f"{API_BASE_URL}/step", json={"action": action})
            
            if step_resp.status_code == 200:
                result = step_resp.json()
                state = result["state"]
                reward = result["reward"]
                done = result["done"]
                total_reward += reward
                print(f"Reward: {reward:+.2f} | Total: {total_reward:.2f}")
            else:
                print(f"Step Error: {step_resp.text}")
                break
            
            time.sleep(0.1)

        print(f"\n[FINISH] Workflow completed in {step_count} steps. Final Reward: {total_reward:.2f}")

    except Exception as e:
        print(f"🚨 Connection Error: {e}")
        print("Check if the server is active on the expected API_BASE_URL.")



if __name__ == "__main__":
    run()