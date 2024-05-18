import json
from timeit import default_timer as timer

from mtsssigner.signer import *

PATH_KEY = "../keys/"
PATH_MSG = "../msg/sign/125_10000.txt"

QTD_ITERATION = 1
HASHES = [
    "SHA256",
    "SHA512",
    "SHA3-256",
    "SHA3-512"
]
SIG_ALGORITHMS = [
    ("PKCS#1 v1.5", "rsa_1024_priv.pem"),
    ("Ed25519", "ed25519_priv.pem"),
    ("Dilithium2", "dilithium_priv.key")
]

K = 3


def main():
    results = {
        "mtss": {
            "PKCS#1 v1.5": {},
            "Ed25519": {},
            "Dilithium2": {},
        },
        "traditional": {
            "PKCS#1 v1.5": {},
            "Ed25519": {},
            "Dilithium2": {},
        }
    }

    with open(PATH_MSG, "rb") as f:
        MESSAGE_BYTES = f.read()

    for sig_algorithm, key_file in SIG_ALGORITHMS:
        if sig_algorithm == "Ed25519":
            sig_scheme = SigScheme(sig_algorithm)
            auxiliar(sig_scheme, sig_algorithm, "SHA512", key_file, results, MESSAGE_BYTES)
            continue

        for hash_function in HASHES:
            sig_scheme = SigScheme(sig_algorithm, hash_function)
            auxiliar(sig_scheme, sig_algorithm, hash_function, key_file, results, MESSAGE_BYTES)

    # save results as json
    with open("results.json", "w") as f:
        json.dump(results, f, indent=4)


def auxiliar(sig_scheme: SigScheme, sig_algorithm: str, hash_function: str, key_file: str, results: dict,
             message_bytes: bytes):
    PRIVATE_KEY = sig_scheme.get_private_key(PATH_KEY + key_file)

    for i in range(QTD_ITERATION):
        # MTSS
        arguments = pre_sign(sig_scheme, PATH_MSG, PATH_KEY + key_file, K)
        start = timer()
        signature = sign_raw(*arguments)
        end = timer()
        if hash_function not in results['mtss'][sig_algorithm]:
            results['mtss'][sig_algorithm][hash_function] = {
                'time': 0,
                'size': 0
            }
        results["mtss"][sig_algorithm][hash_function]['time'] += end - start
        results["mtss"][sig_algorithm][hash_function]['size'] += len(signature)

        # traditional
        start = timer()
        signature = sig_scheme.sign(PRIVATE_KEY, message_bytes)
        end = timer()
        if hash_function not in results['traditional'][sig_algorithm]:
            results['traditional'][sig_algorithm][hash_function] = {
                'time': 0,
                'size': 0
            }
        results["traditional"][sig_algorithm][hash_function]['time'] += end - start
        results["traditional"][sig_algorithm][hash_function]['size'] += len(signature)


if __name__ == "__main__":
    main()
