import hashlib
import traceback
from typing import Dict, Callable, Union

import oqs
from Crypto.Hash import SHA256, SHA512, SHA3_256, SHA3_512
from Crypto.PublicKey import RSA, ECC
from Crypto.PublicKey.ECC import EccKey
from Crypto.PublicKey.RSA import RsaKey
from Crypto.Signature import pkcs1_15, eddsa

import mtsssigner.logger as logger

SCHEME_NOT_SUPPORTED = ("Signature algorithms must be 'PKCS#1 v1.5' or 'Ed25519' or 'Dilithium2' or 'Dilithium3' or "
                        "'Dilithium5'")


class Blake2bHash:
    oid = '1.3.6.1.4.1.1722.12.2.1.16'
    algorithm = hashlib.blake2b

    content: bytes

    def __init__(self, content: bytes):
        self.content = content

    def digest(self):
        return self.algorithm(self.content).digest()


class Blake2sHash:
    oid = '1.3.6.1.4.1.1722.12.2.2.8'
    algorithm = hashlib.blake2s

    content: bytes

    def __init__(self, content: bytes):
        self.content = content

    def digest(self):
        return self.algorithm(self.content).digest()


class SigScheme:
    sig_algorithm: str
    signature_length_bytes: int
    hash_function: str
    digest_size: int
    digest_size_bytes: int
    hash: Dict[str, Callable]
    get_pub_key: Dict[str, Callable]
    get_priv_key: Dict[str, Callable]

    def __init__(self, algorithm: str, hash_function: str = "SHA512"):
        self.get_priv_key = {
            "PKCS#1 v1.5": get_rsa_private_key_from_file,
            "Ed25519": get_ed25519_private_key_from_file,
            "Dilithium2": get_dilithium_private_key_from_file,
            "Dilithium3": get_dilithium_private_key_from_file,
            "Dilithium5": get_dilithium_private_key_from_file,
        }
        self.get_pub_key = {
            "PKCS#1 v1.5": RSA.import_key,
            "Ed25519": ECC.import_key,
        }
        self.hash = {
            "SHA256": SHA256.new,
            "SHA512": SHA512.new,
            "SHA3-256": SHA3_256.new,
            "SHA3-512": SHA3_512.new,
            "BLAKE2B": Blake2bHash,
            "BLAKE2S": Blake2sHash,
        }
        if algorithm not in self.get_priv_key.keys():
            raise ValueError(SCHEME_NOT_SUPPORTED)
        if hash_function not in self.hash.keys():
            raise ValueError("Hashing algorithms must be 'SHA256', 'SHA512', 'SHA3-256', 'SHA3-512', 'BLAKE2B' or 'BLAKE2S'")
        self.sig_algorithm = algorithm
        self.hash_function = hash_function

        # get hash function size
        if self.hash_function == "BLAKE2B":
            self.digest_size = 512
        elif self.hash_function == "BLAKE2S":
            self.digest_size = 256
        else:
            self.digest_size = int(hash_function[-3:])

        # set signature and digest size in bytes
        self.signature_length_bytes = 0
        self.digest_size_bytes = int(self.digest_size / 8)

    def get_digest(self, content: Union[str, bytes]) -> bytes:
        if isinstance(content, str):
            content = content.encode()
        return self.hash[self.hash_function](content).digest()

    def sign(self, private_key: Union[RsaKey, EccKey, bytes], content: Union[bytes, bytearray]) -> bytes:
        hash_now = self.hash[self.hash_function](content)
        if self.sig_algorithm == "PKCS#1 v1.5":
            return pkcs1_15.new(private_key).sign(hash_now)
        elif self.sig_algorithm == "Ed25519":
            return eddsa.new(private_key, 'rfc8032').sign(hash_now)
        elif self.sig_algorithm.startswith("Dilithium"):
            with oqs.Signature(self.sig_algorithm, private_key) as signer:
                return signer.sign(hash_now.digest())
        else:
            raise ValueError(SCHEME_NOT_SUPPORTED)

    def verify(self, public_key: Union[RsaKey, EccKey, bytes], content: Union[bytearray, bytes], signature: bytes) -> bool:
        hash_now = self.hash[self.hash_function](content)
        if self.sig_algorithm == "PKCS#1 v1.5":
            try:
                pkcs1_15.new(public_key).verify(hash_now, signature)
                return True
            except ValueError:
                logger.log_error(traceback.print_exc)
                return False
        elif self.sig_algorithm == "Ed25519":
            try:
                eddsa.new(public_key, 'rfc8032').verify(hash_now, signature)
                return True
            except ValueError:
                logger.log_error(traceback.print_exc)
                return False
        elif self.sig_algorithm.startswith("Dilithium"):
            try:
                with oqs.Signature(self.sig_algorithm) as verifier:
                    return verifier.verify(hash_now.digest(), signature, public_key)
            except (TypeError, ValueError, SystemError):
                logger.log_error(traceback.print_exc)
                return False
        else:
            raise ValueError(SCHEME_NOT_SUPPORTED)

    def get_private_key(self, key_path: str) -> Union[RsaKey, EccKey, bytes]:
        private_key = self.get_priv_key[self.sig_algorithm](key_path)
        self.set_signature_length_bytes(private_key)
        return private_key

    def get_public_key(self, key_path: str) -> Union[RsaKey, EccKey]:
        if self.sig_algorithm.startswith("Dilithium"):
            with open(key_path, "rb") as key_file:
                public_key = key_file.read()
        else:
            with open(key_path, "r", encoding="utf=8") as key_file:
                public_key_str: str = key_file.read()
            public_key = self.get_pub_key[self.sig_algorithm](public_key_str)

        self.set_signature_length_bytes(public_key)
        return public_key

    def set_signature_length_bytes(self, key: Union[RsaKey, EccKey, bytes]) -> None:
        if self.sig_algorithm == "PKCS#1 v1.5":
            self.signature_length_bytes = int(key.n.bit_length() / 8)
        elif self.sig_algorithm == "Ed25519":
            self.signature_length_bytes = 64

        # https://openquantumsafe.org/liboqs/algorithms/sig/dilithium.html
        elif self.sig_algorithm == "Dilithium2":
            self.signature_length_bytes = 2420
        elif self.sig_algorithm == "Dilithium3":
            self.signature_length_bytes = 3293
        elif self.sig_algorithm == "Dilithium5":
            self.signature_length_bytes = 4595


def get_rsa_private_key_from_file(private_key_path: str) -> RsaKey:
    with open(private_key_path, "r", encoding="utf=8") as key_file:
        file_string = key_file.read()
        return RSA.import_key(file_string, None)


def get_ed25519_private_key_from_file(private_key_path: str) -> EccKey:
    with open(private_key_path, "r", encoding="utf=8") as key_file:
        file_string = key_file.read()
        return ECC.import_key(file_string, None)


# Retrieves a private key from bytes in a file
def get_dilithium_private_key_from_file(private_key_path: str) -> bytes:
    with open(private_key_path, "rb") as key_file:
        return key_file.read()
