from server.environment import WarehouseEnv
from server.tasks import easy_task


def test_environment():

    print("Testing Warehouse Environment...")

    task_config = easy_task()

    env = WarehouseEnv(task_config)

    state = env.reset()

    print("Reset successful ✅")

    done = False

    steps = 0

    while not done and steps < 10:

        state, reward, done, _ = env.step("wait")

        steps += 1

    print("Step execution successful ✅")

    print("Environment test PASSED 🚀")


if __name__ == "__main__":

    test_environment()