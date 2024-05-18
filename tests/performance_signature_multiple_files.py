import json
from timeit import default_timer as timer

from mtsssigner.signer import *

QTD_ITERATION = 1

K = 4
HASH_FUNCTION = "SHA256"
SIG_ALGORITHM = "PKCS#1 v1.5"

KEY_FILE = "../keys/rsa_2048_priv.pem"

MESSAGE_PATH = "../msg/sign/q/"
MESSAGE_EXTENSION = ".txt"
MESSAGES = [
    "2401",
    # "4096",
    # "14641",
    # "28561",
]


def main():
    results = {}
    sig_scheme = SigScheme(SIG_ALGORITHM, HASH_FUNCTION)

    for i in range(QTD_ITERATION):
        for message in MESSAGES:
            file_path = MESSAGE_PATH + message + MESSAGE_EXTENSION
            arguments = pre_sign(sig_scheme, file_path, KEY_FILE, K)

            start = timer()
            sign_raw(*arguments)
            end = timer()
            diff_time = end - start

            if file_path not in results:
                results[file_path] = {
                    "time": 0
                }
            results[file_path]["time"] += diff_time

    # save result in json
    with open("results-signature-performance_signature_multiple_files.json", "w") as f:
        json.dump(results, f, indent=4)


if __name__ == "__main__":
    main()
