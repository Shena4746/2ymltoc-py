import os
import sys

import pytest
import regex
from regex import Pattern

sys.path.append(os.path.join(".", "scr"))

from Header_Detecter import Header_Detecter
from scr.Header_Detecter import Header_Detecter
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
def data_multi_digit_pattern_ok() -> list[str]:
    h = Header_Detecter(Text_Lines())
    return [
        f"{symbol}{d}{sep}{d} some text" for sep in h.seps for d in ["1", "15"] for symbol in ["A", "B.", "AP.", ""]
    ]


@pytest.fixture
def data_multi_digit_pattern_ok_with_no_trailing_space() -> list[str]:
    h = Header_Detecter(Text_Lines())
    return [f"{symbol}{d}{sep}{d}some text" for sep in h.seps for d in ["1", "15"] for symbol in ["A", "B.", "AP.", ""]]


@pytest.fixture
def data_multi_digit_pattern_ng_by_too_long_symbols() -> list[str]:
    h = Header_Detecter(Text_Lines())
    return [
        f"{symbol}{d}{sep}{d}some text"
        for sep in h.seps
        for d in ["1", "15", "IX", "V"]
        for symbol in ["Trace", "Introduction", "hoge"]
    ]


@pytest.fixture
def data_mono_digit_pattern_ok() -> list[str]:
    h = Header_Detecter(Text_Lines())
    return [
        f"{symbol}{d}{s} some text"
        for s in h._generate_mono_digit_seps()
        for d in ["1", "15"]
        for symbol in ["A", "B.", ""]
    ]


# -----------------------------------------


def test_multi_digit_pattern_ok(
    data_multi_digit_pattern_ok,
):
    h = Header_Detecter(Text_Lines())
    for data in data_multi_digit_pattern_ok:
        print(data)
        assert validate(h._generate_multi_digit_patterns(), data, True)


def test_mono_digit_pattern_ok(
    data_mono_digit_pattern_ok,
):
    h = Header_Detecter(Text_Lines())
    for data in data_mono_digit_pattern_ok:
        print(data)
        assert validate(h._generate_multi_digit_patterns(), data, False)


def test_multi_digit_pattern_ok_with_no_trailing_space(
    data_multi_digit_pattern_ok_with_no_trailing_space,
):
    h = Header_Detecter(Text_Lines())
    for data in data_multi_digit_pattern_ok_with_no_trailing_space:
        print(data)
        assert validate(h._generate_multi_digit_patterns(), data, True)


def test_multi_digit_pattern_ng_by_too_long_symbols(
    data_multi_digit_pattern_ng_by_too_long_symbols,
):
    h = Header_Detecter(Text_Lines())
    for data in data_multi_digit_pattern_ng_by_too_long_symbols:
        print(data)
        assert validate(h._generate_multi_digit_patterns(), data, False)
