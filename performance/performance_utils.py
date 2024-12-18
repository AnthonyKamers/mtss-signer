# procedure necessary to import from root
import sys

sys.path.append('.')


# https://stackoverflow.com/questions/41383787/round-down-to-2-decimal-in-python
def round_down(value, decimals):
    factor = 1 / (10 ** decimals)
    return (value // factor) * factor


def to_ms(start, end):
    return round_down((end - start) * 1000, 4)
