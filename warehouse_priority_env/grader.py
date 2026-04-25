def calculate_score(env) -> float:
    total_orders = len(env.orders)
    shipped_orders = env.shipped_orders
    time_remaining = env.time_left
    total_time = env.time_limit

    completion_score = shipped_orders / total_orders
    time_score = time_remaining / total_time

    final_score = 0.7 * completion_score + 0.3 * time_score
    return max(0.01, min(0.99, final_score))

