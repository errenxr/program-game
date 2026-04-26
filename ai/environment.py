def get_performance_category(persentase):
    if persentase < 50:
        return "rendah"
    elif persentase < 80:
        return "cukup"
    else:
        return "tinggi"


def get_state(level, persentase):
    performa = get_performance_category(persentase)

    state_mapping = {
        ("mudah", "rendah"): "S0",
        ("mudah", "cukup"): "S1",
        ("mudah", "tinggi"): "S2",

        ("sedang", "rendah"): "S3",
        ("sedang", "cukup"): "S4",
        ("sedang", "tinggi"): "S5",

        ("susah", "rendah"): "S6",
        ("susah", "cukup"): "S7",
        ("susah", "tinggi"): "S8",
    }

    return state_mapping[(level, performa)]


def get_reward(persentase, level, action):
    performa = get_performance_category(persentase)
    
    # Reward dasar berdasarkan performa
    base_reward = 10 if persentase >= 80 else (5 if persentase >= 50 else -5)
    
    # Bonus/penalti berdasarkan ketepatan keputusan
    if performa == "tinggi" and action == "naik":
        bonus = +5   # keputusan tepat: naikkan tantangan
    elif performa == "tinggi" and action == "turun":
        bonus = -8   # keputusan salah: terlalu mudah
    elif performa == "rendah" and action == "turun":
        bonus = +5   # keputusan tepat: turunkan kesulitan
    elif performa == "rendah" and action == "naik":
        bonus = -8   # keputusan salah: terlalu sulit
    elif performa == "cukup" and action == "tetap":
        bonus = +3   # keputusan tepat: pertahankan
    else:
        bonus = 0
    
    return base_reward + bonus


def apply_action(level, action):
    levels = ["mudah", "sedang", "susah"]
    index = levels.index(level)

    if action == "naik":
        index = min(index + 1, 2)
    elif action == "turun":
        index = max(index - 1, 0)
    # jika 'tetap' → tidak berubah

    return levels[index]