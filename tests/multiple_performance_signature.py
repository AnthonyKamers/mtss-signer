from timeit import default_timer as timer

from mtsssigner.signer import *
from mtsssigner.utils.file_and_block_utils import get_signature_file_path, write_signature_to_file
from mtsssigner.verifier import pre_verify, verify_raw

PATH_KEY = "../keys/"
PATH_MSG = "../msg/sign/q/125_10000.txt"
PATH_1_MODIFIED = "../msg/locate/big/125_10000_1.txt"
MESSAGE_BYTES: None | bytearray | bytes = None

QTD_ITERATION = 100
HASHES = [
    "SHA256",
    "SHA512",
    "SHA3-256",
    "SHA3-512",
    "BLAKE2B",
    "BLAKE2S"
]
SIG_ALGORITHMS = [
    ("PKCS#1 v1.5", "rsa_2048_priv.pem", "rsa_2048_pub.pem"),
    ("PKCS#1 v1.5", "rsa_4096_priv.pem", "rsa_4096_pub.pem"),
    ("Ed25519", "ed25519_priv.pem", "ed25519_pub.pem"),
    ("Dilithium2", "dilithium_2_priv.key", "dilithium_2_pub.key"),
    ("Dilithium3", "dilithium_3_priv.key", "dilithium_3_pub.key"),
    ("Dilithium5", "dilithium_5_priv.key", "dilithium_5_pub.key"),
]

K = 3


def main():
    global MESSAGE_BYTES

    with open(PATH_MSG, "rb") as f:
        MESSAGE_BYTES = f.read()

    for alg, priv, pub in SIG_ALGORITHMS:
        if alg == "Ed25519":
            sig_scheme = SigScheme(alg)
            aux(sig_scheme, priv, pub)
            continue

        for hash_function in HASHES:
            sig_scheme = SigScheme(alg, hash_function)
            aux(sig_scheme, priv, pub)


def aux(sig_scheme: SigScheme, path_priv: str, path_pub: str):
    sign_mtss_test(sig_scheme, path_priv)
    verify_mtss_test(sig_scheme, path_pub)
    locate_mtss_test(sig_scheme, path_pub)
    sign_raw_test(sig_scheme, path_priv)
    verify_raw_test(sig_scheme, path_pub)


def sign_mtss_test(sig_scheme: SigScheme, priv: str):
    log_begin(sig_scheme, "sign-mtss", priv)
    results = []
    for i in range(QTD_ITERATION):
        arguments = pre_sign(sig_scheme, PATH_MSG, PATH_KEY + priv, K)
        start = timer()
        signature = sign_raw(*arguments)
        end = timer()

        results.append(end - start)

        # save in disk the last signature
        if i == QTD_ITERATION - 1:
            write_signature_to_file(signature, PATH_MSG)

    write_statistics_to_file(sig_scheme, priv, "sign-mtss", results)
    log_end(sig_scheme, "sign-mtss", priv)


def verify_mtss_test(sig_scheme: SigScheme, pub, path_verify=PATH_MSG, operation="verify-mtss"):
    log_begin(sig_scheme, operation, pub)
    PATH_SIGNED = get_signature_file_path(PATH_MSG, is_raw=False)

    results = []
    for i in range(QTD_ITERATION):
        arguments = pre_verify(path_verify, PATH_SIGNED, sig_scheme, PATH_KEY + pub)
        start = timer()
        result, modified_blocks = verify_raw(*arguments)

        if not result:
            raise Exception("Signature verification is invalid")

        end = timer()

        results.append(end - start)

    write_statistics_to_file(sig_scheme, pub, operation, results)
    log_end(sig_scheme, operation, pub)


def locate_mtss_test(sig_scheme: SigScheme, pub):
    verify_mtss_test(sig_scheme, pub, PATH_1_MODIFIED, "locate-mtss")


def sign_raw_test(sig_scheme: SigScheme, priv):
    global MESSAGE_BYTES

    log_begin(sig_scheme, "sign-raw", priv)
    PRIVATE_BYTES = sig_scheme.get_private_key(PATH_KEY + priv)

    results = []
    for i in range(QTD_ITERATION):
        start = timer()
        signature = sig_scheme.sign(PRIVATE_BYTES, MESSAGE_BYTES)
        end = timer()

        results.append(end - start)

        # save in disk the last signature
        if i == QTD_ITERATION - 1:
            write_signature_to_file(signature, PATH_MSG, is_raw=True)

    write_statistics_to_file(sig_scheme, priv, "sign-raw", results)
    log_end(sig_scheme, "sign-raw", priv)


def verify_raw_test(sig_scheme: SigScheme, pub):
    log_begin(sig_scheme, "verify-raw", pub)

    PATH_SIGNED = get_signature_file_path(PATH_MSG, is_raw=True)
    with open(PATH_SIGNED, "rb") as f:
        SIGNATURE_BYTES = f.read()

    PUBLIC_BYTES = sig_scheme.get_public_key(PATH_KEY + pub)

    results = []
    for i in range(QTD_ITERATION):
        start = timer()
        result = sig_scheme.verify(PUBLIC_BYTES, MESSAGE_BYTES, SIGNATURE_BYTES)
        end = timer()

        if not result:
            raise Exception("Raw signature verification is invalid")

        results.append(end - start)

    write_statistics_to_file(sig_scheme, pub, "verify-raw", results)
    log_end(sig_scheme, "verify-raw", pub)


def write_statistics_to_file(sig_scheme: SigScheme, key: str, operation, results):
    alg = sig_scheme.sig_algorithm
    hash_function = sig_scheme.hash_function
    key_used = key.split("_")[1]

    with open(f"benchmark_{alg}-{key_used}_{hash_function}_{operation}.txt", "w") as file:
        for line in results:
            file.write(str(line) + "\n")


def log_generic(sig_scheme: SigScheme, operation: str, key: str, status: str):
    alg = sig_scheme.sig_algorithm
    hash_function = sig_scheme.hash_function
    key_used = key.split("_")[1]

    print(f"{status} {operation} with {alg} ({key_used}) and {hash_function}")


def log_begin(sig_scheme: SigScheme, operation: str, key: str):
    log_generic(sig_scheme, operation, key, "Started")


def log_end(sig_scheme: SigScheme, operation: str, key: str):
    log_generic(sig_scheme, operation, key, "Finished")


if __name__ == "__main__":
    main()
