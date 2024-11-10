import functools
import re
from math import sqrt, comb
from multiprocessing import Pool
from typing import List, Tuple, Union

from Crypto.PublicKey.ECC import EccKey
from Crypto.PublicKey.RSA import RsaKey
from numpy import floor

from mtsssigner import logger
from mtsssigner.blocks.Parser import Parser
from mtsssigner.blocks.block_utils import get_parser_for_file
from mtsssigner.cff_builder import (create_cff,
                                    get_k_from_n_and_q,
                                    get_d,
                                    create_1_cff)
from mtsssigner.signature_scheme import SigScheme
from mtsssigner.utils.file_and_block_utils import (rebuild_content_from_blocks,
                                                   read_cff_from_file)

cff: List[List[int]] = [[]]
parser: Union[None, Parser] = None
message: str
blocks: List[str]
block_hashes: List[Union[bytearray, bytes]] = []
hashed_tests: List[Union[bytearray, bytes]] = []
corrected = {}


def clear_globals():
    global cff, message, blocks, block_hashes, hashed_tests, corrected, parser
    cff = [[]]
    parser = None
    message = ""
    blocks = []
    block_hashes = []
    hashed_tests = []
    corrected = {}


def pre_verify(message_file_path: str, signature_file_path: str, sig_scheme: SigScheme, public_key_file_path: str):
    global message, parser

    clear_globals()

    # here, we do not need to parse the file into blocks
    # we only need the blocks for the message if the message was modified
    # this is done in #verify_raw
    parser = get_parser_for_file(message_file_path)
    message = parser.get_content()

    with open(signature_file_path, "rb") as signature_file:
        signature: bytes = signature_file.read()

    public_key = sig_scheme.get_public_key(public_key_file_path)

    return signature, public_key, sig_scheme, message_file_path, public_key_file_path


def verify_raw(signature: bytes, public_key: Union[RsaKey, EccKey],
               sig_scheme: SigScheme, message_file_path, public_key_file_path):
    global message, blocks, hashed_tests, cff, block_hashes, corrected, parser

    t = signature[:-int(sig_scheme.signature_length_bytes)]
    t_signature = signature[-int(sig_scheme.signature_length_bytes):]

    verification_result = sig_scheme.verify(public_key, t, t_signature)
    if not verification_result:
        logger.log_nonmodified_verification_result(
            message_file_path, public_key_file_path, sig_scheme, verification_result)
        return verification_result, []

    message_hash = sig_scheme.get_digest(message)
    signature_message_hash = t[-int(sig_scheme.digest_size_bytes):]

    if signature_message_hash == message_hash:
        verification_result = True
        logger.log_nonmodified_verification_result(
            message_file_path, public_key_file_path, sig_scheme, verification_result)
        return True, []

    # now that we know the message has been modified, we need to parse it into blocks
    blocks = parser.parse()
    joined_hashed_tests: bytearray = t[:-int(sig_scheme.digest_size_bytes)]
    hashed_tests = [
        joined_hashed_tests[i:i + int(sig_scheme.digest_size_bytes)]
        for i in range(0, len(joined_hashed_tests), int(sig_scheme.digest_size_bytes))
    ]

    number_of_tests = len(hashed_tests)
    number_of_blocks = len(blocks)

    q: int = int(sqrt(number_of_tests))
    n: int = number_of_blocks
    try:
        k: int = get_k_from_n_and_q(n, q)
        d: int = get_d(q, k)
        try:
            cff = read_cff_from_file(number_of_tests, n, d)
        except IOError:
            if d < 2:
                cff = create_1_cff(n)
            else:
                cff = create_cff(q, k)
    except ValueError as exception:
        if n <= comb(number_of_tests, int(floor(number_of_tests / 2))):
            d = 1
            k = 1
            try:
                cff = read_cff_from_file(number_of_tests, n, d)
            except IOError:
                cff = create_1_cff(n)
        else:
            raise exception

    rebuilt_tests: List[Union[str, bytes]] = []

    if number_of_tests != len(cff):
        logger.log_error(("The number of blocks of the modified message"
                          " is different from the original message."))
        return False, []

    for block in blocks:
        block_hashes.append(sig_scheme.get_digest(block))

    for test in range(number_of_tests):
        concatenation = bytes()
        for block in range(number_of_blocks):
            if cff[test][block] == 1:
                concatenation += block_hashes[block]
        rebuilt_tests.append(concatenation)

    non_modified_blocks: List[int] = []

    for test in range(len(rebuilt_tests)):
        rebuilt_hashed_test = sig_scheme.get_digest(rebuilt_tests[test])
        if rebuilt_hashed_test == hashed_tests[test]:
            for block in range(number_of_blocks):
                if cff[test][block] == 1:
                    non_modified_blocks.append(block)

    modified_blocks = [block for block in range(number_of_blocks)
                       if block not in non_modified_blocks]
    modified_blocks_content = [blocks[block] for block in modified_blocks]
    result = len(modified_blocks) <= d

    logger.log_localization_result(
        message_file_path, public_key_file_path, n, len(cff), d, q,
        k, result, modified_blocks, modified_blocks_content, parser)

    return result, modified_blocks


# Verifies the signature and localizes the modified blocks
# The resulting number of blocks from the supplied file must
# be the same as the one generated by the sign function
def verify(sig_scheme: SigScheme, message_file_path: str, signature_file_path: str,
           public_key_file_path: str) -> Tuple[bool, List[int]]:
    return verify_raw(*pre_verify(message_file_path, signature_file_path, sig_scheme, public_key_file_path))


# Verifies the signature, localizes and corrects the modified blocks. The
# resulting number of blocks from the supplied file must be the same as the
# one generated by the sign function. Also, the correction works better if
# the number of characters of the original values of the modified blocks is
# small (i.e. 4 or less) or the characters of the file are codifiable by 1
# byte (UTF-8 equivalent to ASCII), otherwise the correction takes too long.
def verify_and_correct(verification_result, sig_scheme: SigScheme, message_file_path: str) -> Tuple[bool, List[int], str]:
    correction = ""
    if verification_result[1] == [] or not verification_result[0]:
        return verification_result[0], verification_result[1], correction

    process_pool_size = __available_cpu_count()
    MAX_CORRECTABLE_BLOCK_LEN_CHARACTERS = __get_max_block_length(verification_result[1])
    logger.log_correction_parameters(MAX_CORRECTABLE_BLOCK_LEN_CHARACTERS, process_pool_size)
    for k in verification_result[1]:
        i_rows = []
        modified_blocks_minus_k = set(verification_result[1]) - {k}
        for i in range(len(cff)):
            if cff[i][k] == 1:
                i_rows.append(i)
                for j in modified_blocks_minus_k:
                    if cff[i][j] == 1:
                        i_rows.pop()
                        break
        i = i_rows[0]
        global corrected
        corrected[k] = False

        i_concatenation = []
        k_index = -1
        for block in range(len(cff[i])):
            if cff[i][block] == 1:
                if block != k:
                    i_concatenation.append(block_hashes[block])
                else:
                    k_index = len(i_concatenation)
                    i_concatenation.append(b'0' * sig_scheme.digest_size_bytes)
        k_index = int((k_index * sig_scheme.digest_size) / 8)

        find_correct_b = functools.partial(
            __return_if_correct_b,
            concatenation=bytearray(b''.join(i_concatenation)),
            k_index=k_index, i=i, k=k, sig_scheme=sig_scheme
        )
        with Pool(process_pool_size) as process_pool:
            for result in process_pool.imap(
                    find_correct_b,
                    range(2 ** (MAX_CORRECTABLE_BLOCK_LEN_CHARACTERS * 8))):
                if result is not None:
                    if result[0]:
                        corrected[k] = True
                        blocks[k] = (__int_to_bytes(result[1])).decode("utf-8")
                        logger.log_block_correction(k, blocks[k])
                        break
                    else:
                        logger.log_collision(k, result[1])
                        # Continue executing after collision for partial correction
                        break

    if any(correction for correction in corrected.values()):
        correction = rebuild_content_from_blocks(blocks, message_file_path[-3:])
    else:
        logger.log_block_correction(-1)
    return verification_result[0], verification_result[1], correction


def __get_max_block_length(modified_blocks: List[int]):
    return max([len(blocks[block]) for block in modified_blocks])


# Checks if the given bytes match the original value for the
# modified block k, considering the hash value of the signed ith test
def __return_if_correct_b(b: int, concatenation: bytearray, k_index: int,
                          i: int, k: int, sig_scheme: SigScheme) -> Union[Tuple[bool, int], None]:
    if (b % 500000) == 0:
        logger.log_correction_progress(b)

    hash_k = bytearray(sig_scheme.get_digest(__int_to_bytes(b)))
    concatenation[k_index:(k_index + sig_scheme.digest_size_bytes)] = hash_k
    rebuilt_corrected_test = sig_scheme.get_digest(concatenation)

    if rebuilt_corrected_test == hashed_tests[i]:
        return not corrected[k], b


# Converts an integer to a bytes object
def __int_to_bytes(number: int) -> bytes:
    return number.to_bytes((len(bin(number)[2:]) + 7) // 8, 'big')


# Return the number of cores (physycal of virtual) available for use by the program process
# https://stackoverflow.com/questions/1006289/how-to-find-out-the-number-of-cpus-using-python
def __available_cpu_count():
    """ Number of available virtual or physical CPUs on this system, i.e.
    user/real as output by time(1) when called with an optimally scaling
    userspace-only program"""

    # cpuset
    # cpuset may restrict the number of *available* processors
    try:
        m = re.search(r'(?m)^Cpus_allowed:\s*(.*)$',
                      open('/proc/self/status').read())
        if m:
            res = bin(int(m.group(1).replace(',', ''), 16)).count('1')
            if res > 0:
                return res
    except IOError:
        pass

    # Python 2.6+
    try:
        import multiprocessing
        return multiprocessing.cpu_count()
    except (ImportError, NotImplementedError):
        pass

    # Linux
    try:
        res = open('/proc/cpuinfo').read().count('processor\t:')

        if res > 0:
            return res
    except IOError:
        pass

    raise Exception('Can not determine number of CPUs on this system')
