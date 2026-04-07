import os
import httpx
import time
import json
from openai import OpenAI
from typing import Dict, Any

# --- Configuration ---
# The warehouse environment server URL
SERVER_URL = os.getenv("SERVER_URL", "http://localhost:7860")

# LiteLLM Proxy Configuration (Required for Hackathon Submission)
API_BASE_URL = os.getenv("API_BASE_URL")
API_KEY = os.getenv("API_KEY") or os.getenv("OPENAI_API_KEY")

# Initialize OpenAI Client to use the provided proxy
if API_BASE_URL and API_KEY:
    print(f"📡 Using LiteLLM Proxy: {API_BASE_URL}")
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
elif API_KEY:
    print("🔑 Using Standard OpenAI API (Direct)")
    client = OpenAI(api_key=API_KEY)
else:
    print("⚠️ No API Key found. Falling back to SmartHeuristic logic.")
    client = None


def get_heuristic_action(state: Dict[str, Any]) -> str:
    """High-performance decision logic for warehouse optimization."""
    order = state.get("current_order")
    inventory = state.get("inventory", {})
    inspections = state.get("inspection_pending", [])
    returns = state.get("returns_pending", [])
    packed = state.get("packed_orders", 0)
    shipped = state.get("shipped_orders", 0)

    if packed > shipped:
        return "ship_order"
    
    if inspections:
        # Prioritize restocking items needed for the current order
        if order:
            for item in inspections:
                if order.get(item, 0) > 0:
                    return f"restock_{item}"
        return f"restock_{inspections[0]}"
    
    if order:
        target_product = None
        for product, needed_count in order.items():
            if needed_count > 0:
                if inventory.get(product, 0) > 0:
                    target_product = product
                    break
        
        if target_product:
            return f"pick_{target_product}"
        elif all(v == 0 for v in order.values()):
            return "pack_order"
        elif returns:
            return "inspect_return"
    
    if returns:
        return "inspect_return"
        
    return "wait"


def get_llm_action(state: Dict[str, Any]) -> str:
    """Uses OpenAI API to determine the best next action based on environment state."""
    if not client:
        return get_heuristic_action(state)

    prompt = f"""
    You are a Warehouse Optimization Agent. Your goal is to maximize shipped orders and minimize time.
    Current State: {json.dumps(state, indent=2)}
    
    Available Actions:
    - pick_<item_name> (if in current_order and inventory > 0)
    - pack_order (if all items in current_order are 0)
    - ship_order (if packed_orders > shipped_orders)
    - inspect_return (if returns_pending > 0)
    - restock_<item_name> (if in inspection_pending)
    - wait
    
    Respond with ONLY the action string.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"⚠️ LLM Error: {e}. Falling back to heuristic.")
        return get_heuristic_action(state)


def run_episode(difficulty: str = "easy"):
    print(f"\n🚀 Starting Task: {difficulty.upper()}")
    print(f"[START] task={difficulty}", flush=True)
    
    try:
        # Reset
        resp = httpx.post(f"{SERVER_URL}/reset", params={"difficulty": difficulty})
        state = resp.json()# Note: /reset returns {"state": {...}} or just {...} depending on backend
        if "state" in state: state = state["state"]
        
        done = False
        total_reward = 0
        steps = 0
        
        while not done and steps < 100:
            steps += 1
            action = get_llm_action(state)
            
            step_resp = httpx.post(f"{SERVER_URL}/step", json={"action": action})
            if step_resp.status_code != 200:
                print(f"❌ Error: {step_resp.text}")
                break
                
            data = step_resp.json()
            # Handle both raw (dict) and wrapped (Observation) formats
            state = data.get("observation", data.get("state", {}))
            reward = data.get("reward", 0)
            done = data.get("done", False)
            total_reward += reward
            
            print(f"Step {steps:02} | Action: {action.ljust(15)} | Reward: {reward:+.2f} | Total: {total_reward:.2f}")
            print(f"[STEP] step={steps} reward={reward}", flush=True)
            time.sleep(0.05)
            
        print(f"🏁 Task {difficulty} Finished. Final Score: {total_reward:.2f}")
        print(f"[END] task={difficulty} score={total_reward} steps={steps}", flush=True)
        return total_reward

    except Exception as e:
        print(f"🚨 Connection Error: {e}")
        return 0


def main():
    print("="*40)
    print("      WAREHOUSE OPTIMIZATION BASELINE      ")
    print("="*40)
    
    results = {}
    for diff in ["easy", "medium", "hard"]:
        results[diff] = run_episode(diff)
        time.sleep(1)
        
    print("\n" + "="*40)
    print("SUMMARY RESULTS")
    for diff, score in results.items():
        print(f"{diff.capitalize()}: {score:.2f}")
    print("="*40)


if __name__ == "__main__":
    main()