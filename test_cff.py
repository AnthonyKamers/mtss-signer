import sys
from timeit import default_timer as timer

from mtsssigner.cff_builder import *

k_s = [2, 3, 4, 5]
q_s = [2, 3, 4, 5, 7, 8, 9, 11, 13, 16]


def cff_test(q, k):
    try:
        start = timer()
        create_cff(q, k)
        end = timer()

        print(q, end=" ", flush=True)
        print(k, end=" ", flush=True)
        print(end - start, flush=True)
        sys.stdout.flush()
    except Exception as e:
        print(f"({q},{k}) error in", str(e))


def main():
    for k in k_s:
        for q in q_s:
            cff_test(q, k)


if __name__ == "__main__":
    main()
