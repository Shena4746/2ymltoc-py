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


def hit(pats: list[Pattern], text: str) -> bool:
    return any(regex.search(pat, text) is not None for pat in pats)


@pytest.fixture
def data_mono_digit_pattern_ok() -> list[str]:
    h = Header_Detecter(Text_Lines())
    return [
        f"{symbol}{d}{s} some text"
        for s in h._generate_mono_digit_seps()
        for d in ["1", "15"]
        for symbol in ["A", "B.", ""]
    ]


@pytest.fixture
def data_mono_digit_pattern_ng_by_no_trailing_space() -> list[str]:
    h = Header_Detecter(Text_Lines())
    return [
        f"{symbol}{d}{s}no-space some text"
        for s in h._generate_mono_digit_seps()
        for d in ["1", "15", "IX", "V"]
        for symbol in ["Trace", "Introduction", "hoge"]
    ]


@pytest.fixture
def data_mono_digit_pattern_ng_by_too_long_symbols() -> list[str]:
    h = Header_Detecter(Text_Lines())
    return [
        f"{symbol}{d}{s} no-space some text"
        for s in h._generate_mono_digit_seps()
        for d in ["1", "15", "IX", "V"]
        for symbol in ["Trace", "Introduction", "hoge"]
    ]


@pytest.fixture
def data_multi_digit_pattern_ok() -> list[str]:
    h = Header_Detecter(Text_Lines())
    return [
        f"{symbol}{d}{sep}{d} some text"
        for sep in h.seps
        for d in ["1", "15", "IX", "V"]
        for symbol in ["A", "B.", "AP.", ""]
    ]


# ---------------------------------------------


def test_mono_digit_pattern_ok(data_mono_digit_pattern_ok):
    h = Header_Detecter(Text_Lines())
    print(h._generate_mono_digit_patterns())
    for data in data_mono_digit_pattern_ok:
        print(data)
        assert hit(h._generate_mono_digit_patterns(), data)


def test_mono_digit_pattern_ng_by_no_trailing_space(data_mono_digit_pattern_ng_by_no_trailing_space):
    h = Header_Detecter(Text_Lines())
    print(h._generate_mono_digit_patterns())
    for data in data_mono_digit_pattern_ng_by_no_trailing_space:
        print(data)
        assert not hit(h._generate_mono_digit_patterns(), data)


def test_mono_digit_pattern_ng_by_too_long_symbols(
    data_mono_digit_pattern_ng_by_too_long_symbols,
):
    h = Header_Detecter(Text_Lines())
    print(h._generate_mono_digit_patterns())
    for data in data_mono_digit_pattern_ng_by_too_long_symbols:
        print(data)
        assert not hit(h._generate_mono_digit_patterns(), data)


def test_multi_digit_pattern_ok(
    data_multi_digit_pattern_ok,
):
    h = Header_Detecter(Text_Lines())
    print(h._generate_mono_digit_patterns())
    for data in data_multi_digit_pattern_ok:
        print(data)
        assert not hit(h._generate_mono_digit_patterns(), data)
