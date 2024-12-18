import json
from typing import Tuple

D_TABLE = "data/d_cff.json"
D_FILE = None


def get_parameters_polynomial_cff(d: int, n_from_file: int) -> Tuple[int, int, int, int]:
    global D_FILE

    if D_FILE is None:
        raise Exception("You need to call parse_file() before calling this function")

    if str(d) not in D_FILE:
        raise Exception(f"We currently do not support values with d = {d}")

    for q, k, n, t in D_FILE[str(d)]:
        if n >= n_from_file:
            return q, k, n, t


# this need to be loaded before any operation (speed reasons: to avoid I/O operations)
def parse_file():
    global D_FILE

    D_FILE = json.loads(open(D_TABLE, 'r').read())
