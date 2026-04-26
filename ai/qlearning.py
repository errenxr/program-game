def update_q_value(q_table, state, action, reward, next_state,
                   learning_rate, discount_factor, actions):
    """
    Update Q-table menggunakan rumus Q-Learning
    """

    current_q = q_table[state][action]

    # ambil nilai maksimum di next state
    max_future_q = max(q_table[next_state][a] for a in actions)

    # rumus Q-learning
    new_q = current_q + learning_rate * (
        reward + discount_factor * max_future_q - current_q
    )

    q_table[state][action] = new_q

    return new_q, current_q, max_future_q