from db.db import MessageInfo, BlockHashes
from db import db
from signature_scheme import SigScheme
from verifier import get_cff


def verifier_piece(message_hash: bytes, index_block: int, block_hash: bytes):
    db.db.connect()

    # first check: if the block hash is the same as the one stored in the database
    block_hash_db = BlockHashes.get(BlockHashes.h_m == message_hash, BlockHashes.index == index_block).block_hash
    if block_hash_db != block_hash:
        print('Block hash is different from the one stored in the database')
        return False

    # second check: remount cff and check if the block is in the cff
    message_info = MessageInfo.get(MessageInfo.h_m == message_hash)
    sig_scheme = SigScheme(message_info.scheme, message_info.hash_function)

    signature = message_info.signature

    t = signature[:-int(sig_scheme.signature_length_bytes)]

    joined_hashed_tests: bytearray = t[:-int(sig_scheme.digest_size_bytes)]
    hashed_tests = [
        joined_hashed_tests[i:i + int(sig_scheme.digest_size_bytes)]
        for i in range(0, len(joined_hashed_tests), int(sig_scheme.digest_size_bytes))
    ]

    number_of_tests = len(hashed_tests)
    number_of_blocks = message_info.n

    cff, k, n, d, q = get_cff(number_of_tests, number_of_blocks)
    cff_index = next(filter(lambda x: x[index_block == 1], cff))

    tests = cff[cff_index]
    for test in tests:
        concatenation = bytes()
        for block_now in range(n):
            if test[block_now] == 1:
                concatenation += BlockHashes.get(BlockHashes.h_m == message_hash,
                                                 BlockHashes.index == block_now).block_hash
        test_hash = sig_scheme.get_digest(concatenation)
        if test_hash == hashed_tests[tests.index(test)]:
            return True


if __name__ == "__main__":
    sig_scheme = SigScheme("PKCS#1 v1.5", "BLAKE2B")

    message_hash = (b"o\xb6.\xab\r\x8avg\xc9o\x83\xbeD\x9d\xa4F\xdb\xa9\x00O\x08\x03\x8e\xc6v\xdeuY~\x0b0i\xc5|\x82\xc0"
                    b"\x00\xbc:1A\xcc\x80(\xf9\x89@0)\xdc\x83\xac\xef\xc5\x86\xff5V\xfc\x19sAN\xf9")
    block = b"!"
    index_block = 1

    hash_block = sig_scheme.get_digest(block)

    result = verifier_piece(message_hash, index_block, hash_block)
    print(result)
