import os
import httpx
import time
import json
from openai import OpenAI
from typing import Dict, Any
from server.model import SmartAgent

# --- Configuration ---
# The warehouse environment server URL
SERVER_URL = os.getenv("SERVER_URL", "http://localhost:7860")

# LiteLLM Proxy Configuration (Required for Hackathon Submission)
API_BASE_URL = os.getenv("API_BASE_URL")
API_KEY = os.getenv("API_KEY") or os.getenv("OPENAI_API_KEY")

# Initialize OpenAI Client safely
client = None
if API_BASE_URL and API_KEY:
    try:
        print(f"Using LiteLLM Proxy: {API_BASE_URL}")
        client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    except Exception as e:
        print(f"Failed to initialize OpenAI client with Proxy: {e}")
elif API_KEY:
    try:
        print("Using Standard OpenAI API (Direct)")
        client = OpenAI(api_key=API_KEY)
    except Exception as e:
        print(f"Failed to initialize OpenAI client: {e}")
else:
    print("No API Key found. Falling back to SmartHeuristic logic.")

# Shared heuristic agent instance
_heuristic_agent = SmartAgent()


def get_heuristic_action(state: Dict[str, Any]) -> str:
    """Delegates to SmartAgent for consistent heuristic decisions."""
    return _heuristic_agent.act(state)


def get_llm_action(state: Dict[str, Any]) -> str:
    """Uses OpenAI API to determine the best next action based on environment state."""
    if not client:
        return get_heuristic_action(state)

    prompt = f"""
    You are an Elite Warehouse Optimization AI. Your goal is to achieve a 0.90+ efficiency score.
    Score Formula: 0.7 * (shipped/total) + 0.3 * (time_remaining/total_time).
    
    STRATEGY:
    - EVERY action (including 'wait', 'restock', 'inspect') costs 1 time step and reduces the score.
    - ONLY pick items needed for the 'current_order'.
    - ONLY 'restock' or 'inspect_return' if you are MISSING an item needed for the 'current_order'.
    - 'pack_order' immediately when the current order is ready.
    - 'ship_order' immediately after packing.
    - AVOID 'wait' at all costs.

    Current State: {json.dumps(state)}
    
    Respond with ONLY the action string.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You are a lean logistics expert. Output only valid actions."},
                      {"role": "user", "content": prompt}],
            max_tokens=10,
            temperature=0
        )
        return response.choices[0].message.content.strip().lower()
    except Exception as e:
        print(f"⚠️ LLM Error: {e}. Falling back to heuristic.")
        return get_heuristic_action(state)


def run_episode(difficulty: str = "easy"):
    print(f"\nStarting Task: {difficulty.upper()}")
    print(f"[START] task={difficulty}", flush=True)

    try:
        # Reset
        resp = httpx.post(f"{SERVER_URL}/reset", params={"difficulty": difficulty})
        state = resp.json()  # /reset returns {"state": {...}} or just {...}
        if "state" in state:
            state = state["state"]

        done = False
        total_reward = 0
        steps = 0

        max_steps = state.get("time_limit", 200)
        while not done and steps < max_steps:
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
            time.sleep(0.01)

        # Calculate normalized score for reporting (0 to 1 range)
        shipped = state.get("shipped_orders", 0)
        total_orders = state.get("total_orders", 1)  # Default to 1 to avoid division by zero
        time_left = state.get("time_left", 0)
        time_limit = state.get("time_limit", 1)

        normalized_score = (0.7 * (shipped / total_orders)) + (0.3 * (time_left / time_limit))
        normalized_score = max(0.01, min(0.99, normalized_score))

        print(f"Task {difficulty} Finished. Final Score: {normalized_score:.2f}")
        print(f"[END] task={difficulty} score={normalized_score:.2f} steps={steps}", flush=True)
        return normalized_score

    except Exception as e:
        print(f"Connection Error: {e}")
        return 0


def main():
    print("=" * 40)
    print("      WAREHOUSE OPTIMIZATION BASELINE      ")
    print("=" * 40)

    results = {}
    for diff in ["easy", "medium", "hard"]:
        results[diff] = run_episode(diff)
        time.sleep(1)

    print("\n" + "=" * 40)
    print("SUMMARY RESULTS")
    for diff, score in results.items():
        print(f"{diff.capitalize()}: {score:.2f}")
    print("=" * 40)


if __name__ == "__main__":
    main()