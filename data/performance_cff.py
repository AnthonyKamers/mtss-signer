import sys
from timeit import default_timer as timer

sys.path.append("../")
from mtsssigner.cff_builder import __create_polynomial_cff


def main():
    q = [2, 3, 4, 5, 7, 8, 9, 11, 13, 16]
    k = [2, 3, 4, 5]

    for q_ in q:
        for k_ in k:
            try:
                start = timer()
                __create_polynomial_cff(q_, k_)
                end = timer()
            except:
                continue

            print(f"{q_} {k_} {(end - start) * 1000:.6f}")


if __name__ == "__main__":
    main()
