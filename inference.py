import os
import httpx
import time

API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://localhost:7860"  # Default Docker port for HF Spaces
)


def run():
    print(f"Connecting to: {API_BASE_URL}")
    
    try:
        # 1. Reset Environment
        print("\n[1] Resetting Environment...")
        response = httpx.post(f"{API_BASE_URL}/reset", params={"difficulty": "easy"})
        if response.status_code != 200:
            print(f"Error Resetting: {response.text}")
            return
            
        data = response.json()
        state = data["state"]
        print(f"Initial State: {state}")

        # 2. Perform a few steps
        actions = ["pick_phone", "pack_order", "wait"]
        
        for action in actions:
            print(f"\n[Action] Performing: {action}...")
            # We need to send action as a dict with "action" key to match our FastAPI app
            step_resp = httpx.post(f"{API_BASE_URL}/step", json={"action": action})
            
            if step_resp.status_code == 200:
                result = step_resp.json()
                print(f"Reward: {result.get('reward')}")
                print(f"Done: {result.get('done')}")
            else:
                print(f"Step Error: {step_resp.text}")
            
            time.sleep(0.5)

        print("\n[Result] Workflow completed.")

    except Exception as e:
        print(f"Connection Error: {e}")
        print("Make sure your server is running (locally or on HF).")


if __name__ == "__main__":
    run()