import matplotlib.pyplot as plt
import random
import pandas as pd
from rl_agent import QLearningAgent
from warehouse_priority_env.grid_env import GridWarehouseEnv

def main():
    env = GridWarehouseEnv()
    agent = QLearningAgent()
    
    episodes = 150
    reward_history = []
    
    print(f"Starting training for {episodes} episodes...")
    
    for ep in range(episodes):
        env.reset()
        state = env.get_rl_state()
        done = False
        episode_reward = 0
        
        # Max steps to prevent hanging
        max_steps = 300
        step_count = 0
        
        while not done and step_count < max_steps:
            step_count += 1
            
            # Every 10 steps, maybe add a random task to keep things interesting
            if step_count % 15 == 0:
                env.add_random_task()
            
            # The RL agent selects the strategy for task assignment
            action = agent.choose_action(state, env.rl_actions)
            
            # All robots follow the same strategy for this step
            step_reward = 0
            for robot_id in range(len(env.robots)):
                # Get movement/action based on selected strategy
                move_action = env.intelligent_action(robot_id, rl_action=action)
                _, reward, done = env.step(robot_id, move_action)
                step_reward += reward
                if done:
                    break
            
            next_state = env.get_rl_state()
            agent.update(state, action, step_reward, next_state, env.rl_actions)
            
            state = next_state
            episode_reward += step_reward
            
        reward_history.append(episode_reward)
        if (ep + 1) % 10 == 0:
            print(f"Episode {ep+1}/{episodes} | Reward: {episode_reward}")

    # 1. Generate Baseline (Random Strategy)
    print("Generating baseline performance (Random Strategy)...")
    baseline_rewards = []
    for _ in range(20):
        env.reset()
        done = False
        ep_reward = 0
        while not done:
            action = random.choice(env.rl_actions)
            for robot_id in range(len(env.robots)):
                move_action = env.intelligent_action(robot_id, rl_action=action)
                _, reward, done = env.step(robot_id, move_action)
                ep_reward += reward
                if done: break
        baseline_rewards.append(ep_reward)
    avg_baseline = sum(baseline_rewards) / len(baseline_rewards)

    # 2. Plot and Save Comparison
    plt.figure(figsize=(10, 6))
    plt.plot(reward_history, color='#38bdf8', linewidth=2.5, label='PyTorch DQN Agent')
    plt.axhline(y=avg_baseline, color='#f43f5e', linestyle='--', linewidth=2, label=f'Random Baseline ({int(avg_baseline)})')
    
    # Add smoothing for better visualization
    if len(reward_history) > 10:
        smoothed = pd.Series(reward_history).rolling(window=10).mean()
        plt.plot(smoothed, color='#0ea5e9', linewidth=3, alpha=0.8, label='Learning Trend (MA-10)')

    plt.fill_between(range(len(reward_history)), reward_history, alpha=0.1, color='#38bdf8')
    plt.title("🚀 Learning Progress: PyTorch DQN vs. Random Baseline", fontsize=16, fontweight='bold', pad=25)
    plt.xlabel("Training Episodes", fontsize=12)
    plt.ylabel("Total Reward per Episode", fontsize=12)
    plt.legend(frameon=True, facecolor='white', framealpha=0.9)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.tight_layout()
    plt.savefig("rl_training_curve.png", dpi=150)
    
    print("\nTraining complete!")
    agent.save_q_table("model.pth")
    
    # Save strategy usage from the final training environment
    import json
    with open("strategy_usage_history.json", "w") as f:
        json.dump(env.strategy_usage, f)
        
    print("Training curve saved as 'rl_training_curve.png' and PyTorch model as 'model.pth'.")

if __name__ == "__main__":
    main()
