from pathlib import Path
from typing import Optional

from Formatter import Formatter
from Header_Detecter import Header_Detecter
from Header_Filler import Filler
from Text_Lines import Text_Lines


def save_yaml(
    text: str,
    path_original: Path,
    dir_out: Path,
) -> tuple[Path, bool]:
    if not dir_out.exists():
        dir_out.mkdir(parents=True)
    save_at: Path = dir_out / f"{path_original.stem}.yaml"
    with open(save_at, mode="w") as tf:
        tf.write(text)
    return save_at, save_at.exists()


def to_yml(text_file: Path | str, dir_out: Optional[str | Path], ja: bool = False) -> None:
    file: Path = Path(text_file)
    dir_out = file.parent if dir_out is None else Path(dir_out)
    with open(str(text_file)) as f:
        tls = Text_Lines(f.read())
        detecter = Header_Detecter(lines=tls)
        headers = detecter.choose_headers()
        filler = Filler(tls)
        tls = filler.fill(headers)
        f = Formatter(tls)
        tls = f.format()
        save_yaml(text=tls.to_text(), path_original=file, dir_out=dir_out)
