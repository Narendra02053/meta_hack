import json
import matplotlib.pyplot as plt
from warehouse_env import WarehouseEnv

def train():
    env = WarehouseEnv()
    
    # 1. Initialize Training Variables
    episode_rewards = []
    num_episodes = 100
    max_steps_per_episode = 200 # Safety limit to prevent infinite loops

    # 2. Training Loop
    for episode in range(num_episodes):
        state = env.reset()
        total_reward = 0
        done = False
        step_count = 0
        
        # 3. Multi-Agent Action Loop
        while not done and step_count < max_steps_per_episode:
            for robot in env.robots:
                robot_id = robot["id"]
                
                # Get action
                action = env.sample_action(robot_id)
                
                # Execute step
                state, reward, done = env.step(robot_id, action)
                total_reward += reward
                
                # Break early if the environment finishes mid-loop
                if done:
                    break
            
            step_count += 1
            
        # 4. Store Episode Reward
        episode_rewards.append(total_reward)
        print(f"Episode {episode} Reward: {total_reward}")

    # 5. Plot Reward Curve
    plt.plot(episode_rewards)
    plt.title("Reward Improvement Across Episodes")
    plt.xlabel("Episodes")
    plt.ylabel("Total Reward")
    plt.savefig("reward_curve.png")
    plt.show()

    # 6. Save Reward Data
    with open("reward_history.json", "w") as f:
        json.dump(episode_rewards, f)
        
    print("Training finished! Saved reward_curve.png and reward_history.json")

if __name__ == "__main__":
    train()
