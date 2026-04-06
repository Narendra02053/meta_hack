import os
import requests

API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://localhost:8000"
)

MODEL_NAME = os.getenv(
    "MODEL_NAME",
    "warehouse_priority_env"
)

HF_TOKEN = os.getenv("HF_TOKEN")


def run():

    print("START")

    # Call reset endpoint
    response = requests.post(
        f"{API_BASE_URL}/reset"
    )

    print("STEP")
    print(response.json())

    print("END")


if __name__ == "__main__":
    run()