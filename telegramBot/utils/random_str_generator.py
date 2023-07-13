import random
import string


def gen_string(number_of_elenents=5):
    return ''.join(random.choice(string.digits) for _ in range(number_of_elenents))
