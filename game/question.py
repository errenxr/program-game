import random

def get_num_items(age, level):
    mapping = {
        5: {"mudah": 2, "sedang": 3, "susah": 4},
        6: {"mudah": 3, "sedang": 4, "susah": 5},
        7: {"mudah": 4, "sedang": 5, "susah": 6},
    }
    return mapping[age][level]


def generate_base_images(images, age, level):
    num_items = get_num_items(age, level)
    return random.sample(images, num_items)


def shuffle_question(base_images):
    shuffled = base_images[:]
    random.shuffle(shuffled)
    return shuffled