from timeit import default_timer as timer

from mtsssigner.signer import *

QTD_ITERATION = 1

K = 4
MSG_FILE = "../msg/sign/q/2401.txt"
HASH_FUNCTION = "SHA256"
SIG_ALGORITHM = "PKCS#1 v1.5"

KEY_FILE = "../keys/rsa_2048_priv.pem"


def main():
    total_pre_sign = 0
    total_mtss = 0
    size_signature = 0
    total_traditional = 0

    sig_scheme = SigScheme(SIG_ALGORITHM, HASH_FUNCTION)
    with open(MSG_FILE, "rb") as f:
        MESSAGE_BYTES = f.read()
    PRIVATE_KEY = sig_scheme.get_private_key(KEY_FILE)

    for i in range(QTD_ITERATION):
        # MTSS
        start = timer()
        arguments = pre_sign(sig_scheme, MSG_FILE, KEY_FILE, K)
        end = timer()
        diff_pre_sign = end - start
        total_pre_sign += diff_pre_sign

        start = timer()
        sign_raw(*arguments)
        end = timer()
        diff_mtss = end - start
        total_mtss += diff_mtss

        # traditional
        # start = timer()
        # sig_scheme.sign(PRIVATE_KEY, MESSAGE_BYTES)
        # end = timer()
        # diff_traditional = end - start
        # total_traditional += diff_traditional

    average_pre_sign = total_pre_sign / QTD_ITERATION
    average_mtss = total_mtss / QTD_ITERATION
    average_traditional = total_traditional / QTD_ITERATION
    diff = average_mtss - average_traditional

    print(f'Pre-sign: {average_pre_sign}')
    print(f'MTSS: {average_mtss}')
    print(f'Traditional: {average_traditional}')
    print(f'Diff: {diff}')


if __name__ == "__main__":
    main()
