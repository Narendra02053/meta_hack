import matplotlib.pyplot as plt
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
            agent.update(state, action, step_reward, next_state)
            
            state = next_state
            episode_reward += step_reward
            
        reward_history.append(episode_reward)
        if (ep + 1) % 10 == 0:
            print(f"Episode {ep+1}/{episodes} | Reward: {episode_reward}")

    # Plot and Save
    plt.figure(figsize=(10, 6))
    plt.plot(reward_history, color='#2ecc71', linewidth=2)
    plt.fill_between(range(len(reward_history)), reward_history, alpha=0.2, color='#2ecc71')
    plt.title("Warehouse RL Training Curve: Task Selection Strategy", fontsize=14, pad=20)
    plt.xlabel("Episode", fontsize=12)
    plt.ylabel("Total Reward", fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig("rl_training_curve.png", dpi=150)
    
    print("\nTraining complete!")
    agent.save_q_table("q_table.json")
    
    # Save strategy usage from the final training environment
    import json
    with open("strategy_usage_history.json", "w") as f:
        json.dump(env.strategy_usage, f)
        
    print("Final Q-table size:", len(agent.q_table))
    print("Training curve saved as 'rl_training_curve.png', model as 'q_table.json', and strategy history.")

if __name__ == "__main__":
    main()
