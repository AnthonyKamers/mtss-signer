import os
import statistics
import csv

BENCHMARK_DIR = "./benchmark/"
OPERATIONS = [
    "sign-raw",
    "sign-mtss",
    "verify-raw",
    "verify-mtss",
    "locate-mtss"
]
HASHES = [
    "SHA256",
    "SHA512",
    "SHA3-256",
    "SHA3-512",
    "BLAKE2B",
    "BLAKE2S"
]
ALGORITHMS = [
    'PKCS#1 v1.5-2048',
    'PKCS#1 v1.5-4096',
    'Ed25519',
    'Dilithium2',
    'Dilithium3',
    'Dilithium5'
]
BENCHMARK_ANALYSIS_NAME = "benchmark-analysis-time.csv"


def get_hash_header():
    for hash_now in HASHES:
        yield hash_now + "-average"
        # yield hash_now + "-stddev"


def main():
    results = [["operation", "scheme", *get_hash_header()]]

    for operation in OPERATIONS:
        for alg in ALGORITHMS:
            files_operation_alg = list(
                filter(lambda file_name: operation in file_name and alg in file_name, os.listdir(BENCHMARK_DIR)))
            sort_files = [result for x in HASHES for result in files_operation_alg if x in result]

            result_file = [operation, alg]
            for file in sort_files:
                sum_file = 0
                with open(BENCHMARK_DIR + file, "r") as f:
                    lines = f.readlines()
                    lines = [float(line.replace("\n", "")) * 1000 for line in lines]

                    qtd_lines = len(lines)

                    for line in lines:
                        sum_file += line

                    average = sum_file / qtd_lines
                    stddev = statistics.stdev(lines)

                    result_file.append(round(average, 2))
                    result_file.append(round(stddev, 2))

            results.append(result_file)

    results_to_latex(results)

    # write to file
    csv.writer(open(BENCHMARK_ANALYSIS_NAME, "w")).writerows(results)
    print(f"Results saved in {BENCHMARK_ANALYSIS_NAME}")


def results_to_latex(results):
    for i, result in enumerate(results):
        if i == 0:
            continue

        try:
            operation, alg, sha256, _, sha512, _, sha3_256, _, sha3_512, _, blake2b, _, blake2s, _ = result
            print(operation, alg)
            print(f"{sha256} & {sha512} & {sha3_256} & {sha3_512} & {blake2b} & {blake2s}")
        except ValueError:
            print(result)


if __name__ == "__main__":
    main()
