from pathlib import Path
from typing import Optional

import click

from main import to_yml


@click.command(help="convert text toc into yaml for pdftoc tool.")
@click.argument("text_file", type=click.Path(exists=True))
@click.option(
    "-d",
    "--dirout",
    type=click.Path(file_okay=False),
    help="directory where output file is saved. the default uses the same place as the input text file.",
)
@click.option("--ja", type=bool, is_flag=True, help="detect headers for Japanese literature")
def to_ymltoc(text_file: str | Path, dirout: Optional[str], ja: bool):
    to_yml(text_file=text_file, dir_out=dirout, ja=ja)


if __name__ == "__main__":
    to_ymltoc()
