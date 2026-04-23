from server.environment import WarehouseEnv
from server.tasks import hard_task
from server.grader import calculate_score
from server.model import SmartAgent


task_config = hard_task()
env = WarehouseEnv(task_config)
agent = SmartAgent()

env.reset()
done = False
steps = 0
max_steps = 150

while not done and steps < max_steps:
    action = agent.act(env.get_state())
    state, reward, done, _ = env.step(action)
    steps += 1

score = calculate_score(env)
print("\nHard Task Score:", score)