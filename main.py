import traceback
from datetime import timedelta
from pathlib import Path
from timeit import default_timer as timer
from typing import Callable, Union

import typer
from typing_extensions import Annotated

from mtsssigner import logger
from mtsssigner.logger import print_operation_result
from mtsssigner.signature_scheme import SigScheme, ALGORITHM, HASH
from mtsssigner.signer import pre_sign, sign_raw
from mtsssigner.utils.file_and_block_utils import write_signature_to_file, write_correction_to_file, get_raw_message
from mtsssigner.verifier import pre_verify, verify_raw, verify_and_correct

app = typer.Typer()


def begin_execution(operation: str, algorithm: ALGORITHM, hash_func: HASH, debug: bool) -> SigScheme:
    # evaluate constraints
    if algorithm == ALGORITHM.ED25519 and hash_func != HASH.SHA512:
        raise ValueError("For Ed25519, hash function must be SHA512")

    # enable/disable logger
    logger.enabled = debug

    # initialize SigScheme
    sig_scheme = SigScheme(algorithm, hash_func)

    # logging
    logger.log_execution_start(operation)

    return sig_scheme


def execute_operation(func_operation: Callable, post_execution: Callable, operation: str, message_path: Path,
                      time_only: bool, only_parameters_time: bool):
    try:
        start, end_parameters, end, result = func_operation()

        # check output (time printing or post_execution)
        if time_only:
            if only_parameters_time:
                print(end_parameters - start)
            else:
                print(end - start)
        else:
            post_execution(result)
            print_operation_result(not time_only, operation, str(message_path), result)

        # logging
        logger.log_execution_end(timedelta(seconds=end_parameters - start))
    except Exception as e:
        logger.log_error(traceback.print_exc)
        print(f'Error: {repr(e)}')


@app.command()
def sign(algorithm: ALGORITHM, hash_func: HASH, message_path: Path, private_key_path: Path, k_cff: int,
         time_only: Annotated[bool, "--time-only"] = False, debug: Annotated[bool, "--debug"] = False,
         only_parameters_time: Annotated[bool, "--only-parameters-time"] = False,
         is_raw: Annotated[
             bool, "--raw", typer.Option(help="If the signing should be using traditional scheme")] = False):
    OPERATION = "sign"

    sig_scheme = begin_execution(OPERATION, algorithm, hash_func, debug)

    def sign_actually():
        if is_raw:
            message_content = get_raw_message(str(message_path)).encode()
            private_key = sig_scheme.get_private_key(str(private_key_path))

            start = timer()
            signature = sig_scheme.sign(private_key, message_content)
            end = timer()
            end_parameters = 0
        else:
            start = timer()
            parameters = pre_sign(sig_scheme, str(message_path), str(private_key_path), k_cff)
            end_parameters = timer()
            signature = sign_raw(*parameters)
            end = timer()

        return start, end_parameters, end, signature

    def post_sign(signature):
        write_signature_to_file(signature, str(message_path), is_raw)

    execute_operation(sign_actually, post_sign, OPERATION, message_path, time_only, only_parameters_time)


@app.command()
def verify(algorithm: ALGORITHM, hash_func: HASH, message_path: Path, signature_path: Path, public_key_path: Path,
           time_only: Annotated[bool, "--time-only"] = False, debug: Annotated[bool, "--debug"] = False,
           only_parameters_time: Annotated[bool, "--only-parameters-time"] = False,
           is_raw: Annotated[
               bool, "--raw", typer.Option(help="If the verification should be using traditional scheme")] = False):
    OPERATION = "verify"

    sig_scheme = begin_execution(OPERATION, algorithm, hash_func, debug)

    def verify_actually():
        if is_raw:
            with open(signature_path, "rb") as signature_file:
                signature: Union[bytes, bytearray] = signature_file.read()
            message_content = get_raw_message(str(message_path)).encode()
            public_key = sig_scheme.get_public_key(str(public_key_path))

            start = timer()
            result = sig_scheme.verify(public_key, message_content, signature)
            end = timer()
            end_parameters = 0
        else:
            start = timer()
            parameters = pre_verify(str(message_path), str(signature_path), sig_scheme, str(public_key_path))
            end_parameters = timer()
            result = verify_raw(*parameters)
            end = timer()

        return start, end_parameters, end, result

    def post_verify(result):
        pass

    execute_operation(verify_actually, post_verify, OPERATION, message_path, time_only, only_parameters_time)


@app.command()
def verify_correct(algorithm: ALGORITHM, hash_func: HASH, message_path: Path, signature_path: Path, public_key_path: Path,
                   time_only: Annotated[bool, "--time-only"] = False, debug: Annotated[bool, "--debug"] = False,
                   only_parameters_time: Annotated[bool, "--only-parameters-time"] = False):
    OPERATION = "verify-correct"

    sig_scheme = begin_execution(OPERATION, algorithm, hash_func, debug)

    def verify_correct_actually():
        start = timer()
        verify_result = verify(sig_scheme, str(message_path), str(signature_path), str(public_key_path))
        end_verify = timer()
        result = verify_and_correct(verify_result, sig_scheme, str(message_path))
        end = timer()

        return start, end_verify, end, result

    def post_verify_correct(result):
        correction = result[2]
        if correction != "":
            write_correction_to_file(str(message_path), correction)
            print_operation_result(not time_only, OPERATION, str(message_path), result)
        elif len(result[1]) > 0:
            print(f"File {str(message_path)} could not be corrected")

    execute_operation(verify_correct_actually, post_verify_correct, OPERATION, message_path, time_only,
                      only_parameters_time)


if __name__ == "__main__":
    app()
