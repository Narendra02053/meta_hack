def calculate_score(env):
    total_orders = len(env.orders)
    shipped_orders = env.shipped_orders
    time_remaining = env.time_left
    total_time = env.time_limit

    # Order completion score
    completion_score = shipped_orders / total_orders

    # Time efficiency score
    time_score = time_remaining / total_time

    # Combine scores
    final_score = 0.7 * completion_score + 0.3 * time_score

    # Clamp score strictly between 0 and 1 (Required by platform)
    final_score = max(0.01, min(0.99, final_score))

    return final_score