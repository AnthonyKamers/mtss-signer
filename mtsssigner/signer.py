from typing import Union, Tuple, List

from Crypto.PublicKey.ECC import EccKey
from Crypto.PublicKey.RSA import RsaKey

from mtsssigner import logger
from mtsssigner.blocks.Parser import Parser
from mtsssigner.blocks.block_utils import get_parser_for_file
from mtsssigner.cff_builder import (create_cff,
                                    create_1_cff,
                                    get_t_for_1_cff)
from mtsssigner.cffs.cff_utils import get_parameters_polynomial_cff
from mtsssigner.signature_scheme import SigScheme, D_BYTES_LENGTH, D_BYTES_ORDER
from mtsssigner.utils.file_and_block_utils import read_cff_from_file


# Signs a file using a modification tolerant signature scheme, which
# allows for localization and correction of modifications to the file
# within certain limitations. The number of blocks created from the file
# (their creation depends on the file type) must be a prime power.
# https://crypto.stackexchange.com/questions/95878/does-the-signature-length-of-rs256-depend-on-the-size-of-the-rsa-key-used-for-si
def sign(sig_scheme: SigScheme, message_file_path: str, private_key_path: str, d: int = 0) -> bytearray:
    return sign_raw(*pre_sign(sig_scheme, message_file_path, private_key_path, d))


# deals with IO operations and CFF create/cache read and separating message in blocks
def pre_sign(sig_scheme: SigScheme, message_file_path: str, private_key_path: str, d: int = 0,
             concatenate_strings: bool = False):
    # get blocks from message type specific
    file_parser = get_parser_for_file(message_file_path)
    blocks = file_parser.parse()
    n_from_file = len(blocks)

    # if d=1, use 1-CFF, otherwise use polynomial CFF
    if d == 1:
        n = n_from_file
        t = get_t_for_1_cff(n_from_file)
        q = None
        k = None

        try:
            cff = read_cff_from_file(t, n_from_file, 1)
            logger.log_cff_from_file()
        except IOError:
            cff = create_1_cff(n_from_file)
    else:
        q, k, n_expected, t = get_parameters_polynomial_cff(d, n_from_file)
        n = n_expected

        # if the expected number of blocks in a document is different, then we should create the remnant number of
        # blocks as empty ones. This should happen only when the number of blocks is not a prime power (common).
        if n_expected > n_from_file:
            file_parser.create_empty_blocks(n_expected - n_from_file)

        try:
            cff = read_cff_from_file(t, n_expected, d)
            logger.log_cff_from_file()
        except IOError:
            cff = create_cff(q, k)

    # log about the CFF created/parsed
    logger.log_signature_parameters(message_file_path, private_key_path, n,
                                    sig_scheme, d, t, file_parser, q, k, n_from_file)

    # A d-CFF(t, n) has dimension (t, n)
    cff_dimensions = (t, n)

    # read private key and gets object
    private_key = sig_scheme.get_private_key(private_key_path)

    # return necessary information to sign raw
    return sig_scheme, file_parser, private_key, cff_dimensions, cff, concatenate_strings, d


def sign_raw(sig_scheme: SigScheme, parser: Parser, private_key: Union[RsaKey, EccKey, bytes],
             cff_dimensions: Tuple[int, int], cff: List[List[int]], concatenate_strings: bool,
             d: int) -> bytearray:
    blocks = parser.get_blocks()

    tests = []
    for test in range(cff_dimensions[0]):
        concatenation = bytes()
        for block in range(cff_dimensions[1]):
            if cff[test][block] == 1:
                block_now = blocks[block]

                if concatenate_strings:
                    # if we concatenate the strings, we should have t less hash operations
                    concatenation += str(block_now)
                else:
                    # if we hash each block separately, we should have t hash operations added (the original paper
                    # consider using this way)
                    concatenation += sig_scheme.get_digest(block_now)
        tests.append(concatenation)

    # our final signature is the hash of each test concatenation (T in the original proposal)
    signature = bytearray()
    for test in tests:
        test_hash = sig_scheme.get_digest(test)
        signature += test_hash

    # hash the whole message
    message_hash = sig_scheme.get_digest(parser.get_content())

    # append the message hash to the signature (T[t+1] should be our message hash)
    signature += message_hash

    # append the number of blocks in the message (T[t+2] should be the number of blocks that can be modified)
    signature += d.to_bytes(D_BYTES_LENGTH, D_BYTES_ORDER)

    # we sign the signature (T)
    signed_t = sig_scheme.sign(private_key, signature)
    signature += signed_t

    # the last part of the signature is the number of blocks in the message
    # signature += d.to_bytes(D_BYTES_LENGTH, D_BYTES_ORDER)

    return signature
