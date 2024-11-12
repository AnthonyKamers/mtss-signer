import json
from typing import Tuple

D_TABLE = "data/d_cff.json"


def get_parameters_polynomial_cff(d: int, n_from_file: int) -> Tuple[int, int, int, int]:
    table = parse_file()

    if str(d) not in table:
        raise Exception(f"We currently do not support values with d = {d}")

    for q, k, n, t in table[str(d)]:
        if n >= n_from_file:
            return q, k, n, t


def parse_file():
    return json.loads(open(D_TABLE, 'r').read())
