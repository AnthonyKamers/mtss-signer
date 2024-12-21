import json
from typing import Tuple, List

from mtsssigner.signature_scheme import ALGORITHM, HASH, DIRECTORY_BLOCKS, SigScheme, D_BYTES_LENGTH
from mtsssigner.utils.file_and_block_utils import read_cff_from_file

index_possible_tests = 0
possible_tests = []

CONCATENATE_STRINGS = False


def client():
    def block_ver(m_j, pk, Y):
        signature, i, M, k = Y

        # step 1
        t = signature[:-int(sig_scheme.signature_length_bytes)]
        t_signature = signature[-int(sig_scheme.signature_length_bytes):]

        verification_result = sig_scheme.verify(pk, t, t_signature)
        if not verification_result:
            return False

        t_without_d = t[:-D_BYTES_LENGTH]

        # step 2
        M.insert(k, m_j)

        # step 3
        concatenation = bytes()
        for m in M:
            if CONCATENATE_STRINGS:
                concatenation += str(m)
            else:
                concatenation += sig_scheme.get_digest(m)

        # step 4
        h = sig_scheme.get_digest(concatenation)

        # step 5
        digest_size = sig_scheme.digest_size_bytes
        test_hash = t_without_d[i * digest_size: (i + 1) * digest_size]

        if h != test_hash:
            return False

        return True

    ALGORITHM_USED = ALGORITHM.RSA
    HASH_USED = HASH.SHA256
    sig_scheme = SigScheme(ALGORITHM_USED, HASH_USED)
    PK_USED = "keys/rsa_2048_pub.pem"

    public_key = sig_scheme.get_public_key(PK_USED)

    HASH_MESSAGE = "43a39a552c4d381f0ccba7a5b9ef1d2c19257287b31df8a8ea29b1a330a1fae3"

    BLOCK_0 = "1|sett"
    HASH_BLOCK_0 = "57ce6b405b31af538ae3745c5b9267f1e6ca3c30b2c0fd9d77da818dfe3a5edb"
    INDEX_BLOCK = 0

    X = (HASH_MESSAGE, INDEX_BLOCK)
    Y_server = server(X)

    flag = block_ver(BLOCK_0, public_key, Y_server)
    print(flag)


def server(X: Tuple[str, int]) -> Tuple[bytes, int, List[str], int]:
    def get_blocks_from_test() -> Tuple[List[str], int]:
        # find indexes in which the test is 1
        indexes = [i for i, x in enumerate(test_now) if x == 1]

        # get the value of the blocks (appearing in the indexes and if the index is not j)
        blocks_test = [blocks_file[str(i)] for i in indexes if i != j]
        return blocks_test, indexes.index(j)

    global possible_tests, index_possible_tests

    h_m, j = X

    # read blocks division from disk
    with open(f"{DIRECTORY_BLOCKS}/{h_m}.json", "r") as file:
        file_bytes = file.read()

    # read signature from disk
    with open(f"{DIRECTORY_BLOCKS}/{h_m}.sig", "rb") as file:
        signature = file.read()

    blocks_file = json.loads(file_bytes)

    t, n, d = blocks_file["cff"].values()

    # read CFF from disk
    cff = read_cff_from_file(t, n, d)
    for test in cff:
        if test[j] == 1:
            possible_tests.append(test)

    test_now = possible_tests[index_possible_tests]
    blocks_from_test, k = get_blocks_from_test()

    Y = (signature, index_possible_tests, blocks_from_test, k)

    return Y


if __name__ == "__main__":
    client()
