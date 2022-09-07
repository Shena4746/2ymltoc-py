from __future__ import annotations

from typing_extensions import Self


class Text_Line:
    def __init__(self, text: str = "", idx: int = -1, sep: str = " ", depth: int = -1, has_child: bool = False) -> None:
        self._validate_text(text)
        self._idx: int = idx
        self._text: str = text
        self._sep: str = sep
        self.depth: int = depth
        self.has_child: bool = has_child

    def __lt__(self, other: Self) -> bool:
        return self.idx < other.idx

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}: idx={self.idx}, text={self.to_text()}, depth={self.depth}, has_child={self.has_child}"

    def __len__(self) -> int:
        return len(self.text)

    @property
    def idx(self) -> int:
        return self._idx

    @property
    def sep(self) -> str:
        return self._sep

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, text: str) -> None:
        self._text = text

    @sep.setter
    def sep(self, new_sep: str) -> None:
        self._sep = new_sep

    def is_empty(self) -> bool:
        return self.to_text() == ""

    def is_depth_set(self) -> bool:
        return self.depth != -1

    def to_text(self) -> str:
        return self.text

    def get_instance(self, idx: int, text: str, sep: str) -> Self:
        return Text_Line(idx=idx, text=text, sep=sep)

    def _has_newline(self, text: str) -> bool:
        return len(lines := text.splitlines()) != 0 and lines[0] != text

    def _validate_text(self, text: str) -> bool:
        """text should be free of newline characters"""
        if self._has_newline(text):
            raise ValueError(f"text must admit no newline character. text={text}")
        return True
