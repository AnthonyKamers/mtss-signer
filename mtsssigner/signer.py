from typing import Union, List

from Crypto.PublicKey.ECC import EccKey
from Crypto.PublicKey.RSA import RsaKey

from mtsssigner import logger
from mtsssigner.cff_builder import (create_cff,
                                    get_q_from_k_and_n,
                                    create_1_cff,
                                    get_t_for_1_cff,
                                    get_d)
from mtsssigner.signature_scheme import SigScheme
from mtsssigner.utils.file_and_block_utils import get_message_and_blocks_from_file, read_cff_from_file
from mtsssigner.utils.prime_utils import is_prime_power


# Signs a file using a modification tolerant signature scheme, which
# allows for localization and correction of modifications to the file
# within certain limitations. The number of blocks created from the file
# (their creation depends on the file type) must be a prime power.
# https://crypto.stackexchange.com/questions/95878/does-the-signature-length-of-rs256-depend-on-the-size-of-the-rsa-key-used-for-si
def sign(sig_scheme: SigScheme, message_file_path: str, private_key_path: str,
         max_size_bytes: int = 0, k: int = 0) -> bytearray:
    return sign_raw(*pre_sign(sig_scheme, message_file_path, private_key_path, k))


# deals with IO operations and CFF create/cache read and separating message in blocks
def pre_sign(sig_scheme: SigScheme, message_file_path: str, private_key_path: str, k: int = 0):
    # get blocks from message type specific
    message, blocks = get_message_and_blocks_from_file(message_file_path)
    if not is_prime_power(len(blocks)):
        logger.log_error(("Number of blocks generated must be a prime power "
                          f"to use polynomial CFF (Number of blocks = {len(blocks)}), using 1-CFF"))
        k = 1
    n: int = len(blocks)

    # create/read CFF
    if k == 1:
        try:
            cff = read_cff_from_file(get_t_for_1_cff(n), n, 1)
            logger.log_cff_from_file()
        except IOError:
            cff = create_1_cff(n)
    elif k > 1:
        q = get_q_from_k_and_n(k, n)
        try:
            cff = read_cff_from_file(q ** 2, q ** k, get_d(q, k))
            logger.log_cff_from_file()
        except IOError:
            cff = create_cff(q, k)
    else:
        raise Exception("Either max size or 'K' value must be provided")

    cff_dimensions = (len(cff), n)
    if k > 1:
        d = get_d(q, k)
        logger.log_signature_parameters(message_file_path, private_key_path, n,
                                        sig_scheme, d, len(cff), blocks, q, k, 0)
    else:
        d = 1
        logger.log_signature_parameters(message_file_path, private_key_path, n,
                                        sig_scheme, d, len(cff), blocks)

    # read private key and gets object
    private_key = sig_scheme.get_private_key(private_key_path)

    # return necessary information to sign raw
    return sig_scheme, message, blocks, private_key, cff_dimensions, cff


def sign_raw(sig_scheme: SigScheme, message: str, blocks: List[str], private_key: Union[RsaKey, EccKey, bytes],
             cff_dimensions, cff) -> bytearray:
    tests = []
    for test in range(cff_dimensions[0]):
        concatenation = bytes()
        for block in range(cff_dimensions[1]):
            if cff[test][block] == 1:
                concatenation += sig_scheme.get_digest(blocks[block])
        tests.append(concatenation)

    signature = bytearray()
    for test in tests:
        test_hash = sig_scheme.get_digest(test)
        signature += test_hash
    message_hash = sig_scheme.get_digest(message)
    signature += message_hash

    signed_t = sig_scheme.sign(private_key, signature)
    signature += signed_t

    return signature
