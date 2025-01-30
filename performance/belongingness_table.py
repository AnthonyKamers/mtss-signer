import json
from timeit import default_timer as timer

import typer

from performance_utils import to_ms
from belongingness_protocol import client_1, client_2, server, clear_globals
from mtsssigner.blocks.block_utils import get_parser_for_file
from mtsssigner.cffs.cff_utils import parse_file
from mtsssigner.signature_scheme import ALGORITHM, HASH, SigScheme
from mtsssigner.signer import sign
from mtsssigner.utils.file_and_block_utils import write_signature_to_file
from sig_ver_all import PATH_KEY, PATH_MSG, FILES, D_FILES

QTD_ITERATION = 100
CONCATENATE_STRINGS = True

TABLE_NAME = "belongingness-performance"
OUTPUT_JSON = f"performance/output/{TABLE_NAME}.json"
OUTPUT_TABLE = f"performance/output/{TABLE_NAME}.tex"
LABEL_TABLE = f"table:{TABLE_NAME}"
TABLE_CAPTION = '''Performance overview for the MTSS belongingness protocol. The network delay and the network bandwidth
are not considered; these results are obtained offline. The CFFs for each file are the same as used in Tables 2 and 3. Text
files were used for simplicity. Signed with $\\Sigma$ as ML-DSA level I, and $\\H$ as BLAKE2b.'''

algorithm = ALGORITHM.DILITHIUM2
hash_func = HASH.BLAKE2B
priv = PATH_KEY + "dilithium_2_priv.key"
pub = PATH_KEY + "dilithium_2_pub.key"

BLOCK_MESSAGE = "00000000"
INDEX_BLOCK = 0

data = {}

app = typer.Typer()


@app.command()
def run():
    # necessary to call before the tests
    parse_file()

    for k, file in enumerate(FILES):
        print(f'running file {file}')

        path_file = PATH_MSG + file
        d = D_FILES[k]

        sig_scheme = SigScheme(algorithm, hash_func)

        # sign
        signature = sign(sig_scheme, path_file, priv, d, save_blocks=True, concatenate_strings=CONCATENATE_STRINGS)
        write_signature_to_file(signature, path_file, False)

        # parser
        parser = get_parser_for_file(path_file)

        hash_message = sig_scheme.get_digest(parser.get_content()).hex()

        protocol_performance(hash_message, file)

    generate_output()
    generate_table_latex()


@app.command()
def table_from_file(path: str = OUTPUT_JSON):
    read_from_json(path)
    generate_table_latex()


def read_from_json(path: str):
    global data

    with open(path, "r") as f:
        data = json.load(f)


def protocol_performance(hash_message: str, filename: str):
    global data

    for i in range(QTD_ITERATION):
        start_client_1 = timer()
        X = client_1(algorithm, hash_func, pub, hash_message, BLOCK_MESSAGE, INDEX_BLOCK)
        end_client_1 = timer()

        start_server = timer()
        Y = server(X)
        end_server = timer()

        start_client_2 = timer()
        result = client_2(X, Y, CONCATENATE_STRINGS)
        end_client_2 = timer()

        # clear belongingness protocol globals at each iteration
        clear_globals()

        if not result:
            raise Exception("Block verification failed")

        n_from_filename = filename.split(".")[0]

        # save into data
        if i == 0:
            data[n_from_filename] = {
                "hash": hash_message,
                "blocks_passed": len(Y[2]),
                "client_1": to_ms(start_client_1, end_client_1),
                "server": to_ms(start_server, end_server),
                "client_2": to_ms(start_client_2, end_client_2)
            }
        else:
            data[n_from_filename] = {
                "hash": hash_message,
                "blocks_passed": len(Y[2]),
                "client_1": round((data[n_from_filename]["client_1"] + to_ms(start_client_1, end_client_1)) / 2, 2),
                "server": round((data[n_from_filename]["server"] + to_ms(start_server, end_server)) / 2, 2),
                "client_2": round((data[n_from_filename]["client_2"] + to_ms(start_client_2, end_client_2)) / 2, 2)
            }


def generate_output():
    global data

    with open(OUTPUT_JSON, "w") as f:
        f.write(json.dumps(data, indent=4))


def generate_table_latex():
    global data

    header = '''
    \\begin{table}[ht]
    \\setlength{\\tabcolsep}{10pt}
    \\centering
    \\caption{%s}
    \\begin{tabular}{rcccc}
        \\toprule
        \\multicolumn{1}{c}{\\multirow{2}{*}{$n$}} &
            \\multicolumn{1}{c}{\\multirow{2}{*}{$|M|$ transmitted}} &
            \\multicolumn{3}{c}{Time (ms)} \\\\

        \\cmidrule{3-5}
        & & Client$_1$ & Server$_1$ & Client$_2$ \\\\
        \\cmidrule{1-5}
    ''' % TABLE_CAPTION

    footer = '''
    \t\\bottomrule
        \\end{tabular}
        \\label{%s}
    \\end{table}
    ''' % LABEL_TABLE

    body = ''
    for key, value in data.items():
        body += (f'\t{key} & {value["blocks_passed"]} & {value["client_1"]} & {value["server"]} & {value["client_2"]} '
                 f'\\\\\n')

    with open(OUTPUT_TABLE, "w") as f:
        f.write(header)
        f.write(body)
        f.write(footer)


if __name__ == "__main__":
    app()
