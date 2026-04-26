from ai.agent import Agent
from ai.environment import get_state, get_reward, apply_action

# pakai anak id 1 (bebas, sesuai data kamu)
agent = Agent(1)

# simulasi kondisi anak
level = "mudah"
persentase = 80  # misalnya anak cukup bagus

# step 1: state
state = get_state(level, persentase)

# step 2: pilih action
action = agent.choose_action(state)

# step 3: reward
reward = get_reward(persentase)

# step 4: level baru
next_level = apply_action(level, action)

# step 5: next state
next_state = get_state(next_level, persentase)

# step 6: update Q-table
agent.learn(state, action, reward, next_state)

# debug output
print("=== HASIL TEST AI ===")
print("State:", state)
print("Action:", action)
print("Reward:", reward)
print("Next Level:", next_level)
print("Next State:", next_state)