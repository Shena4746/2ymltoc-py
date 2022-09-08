import os
import sys

import pytest
import regex
from regex import Pattern

sys.path.append(os.path.join(".", "scr"))

from Header_Detecter import Header_Detecter
from scr.Header_Detecter import Header_Detecter_ja as Header_Detecter
from scr.Text_Lines import Text_Lines
from Text_Lines import Text_Lines


def hit_any(pats: list[Pattern], text: str) -> bool:
    return any(regex.search(pat, text) for pat in pats)


def validate(pats: list[Pattern], text: str, should_be: bool) -> bool:
    if hit_any(pats, text) == should_be:
        return True
    # if hit something whereas nothing should be hit, show it
    if should_be is False:
        for pat in pats:
            if regex.search(pat, text) is not None:
                raise ValueError(f"unwanted match! at text={text}, pat={pat}")
    return True


@pytest.fixture
def data_paired_ja_pattern_ok() -> list[str]:
    h = Header_Detecter(Text_Lines())
    digits_kanji = ["〇", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]
    return [f"{p1}{d1}{d2}{p2} some text" for p1, p2 in h.key_paired for d1 in digits_kanji for d2 in digits_kanji] + [
        f"{p1}{d1}{d2}{p2} some text" for p1, p2 in h.key_paired for d1 in range(10) for d2 in range(10)
    ]


# -----------------------------------------


def test_paired_ja_pattern_ok(
    data_paired_ja_pattern_ok,
):
    h = Header_Detecter(Text_Lines())
    for data in data_paired_ja_pattern_ok:
        print(data)
        assert validate(h._generate_paired_patterns(), data, True)
