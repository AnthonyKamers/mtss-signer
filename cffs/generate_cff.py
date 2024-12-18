import typer
import sys

sys.path.append('.')

from mtsssigner.cff_builder import create_1_cff, create_cff
from mtsssigner.utils.file_and_block_utils import write_cff_to_file

app = typer.Typer()


@app.command()
def sperner(n: int):
    cff = create_1_cff(n)
    t = len(cff)

    write_cff_to_file(t, n, 1, cff)


@app.command()
def polynomial(q: int, k: int):
    cff = create_cff(q, k)
    t = len(cff)
    n = len(cff[0])

    write_cff_to_file(t, n, k, cff)


if __name__ == "__main__":
    app()
