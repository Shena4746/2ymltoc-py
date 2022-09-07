import regex

from Header_Detecter import Header
from Text_Lines import Text_Lines


class Filler:
    """fill header metadata into textlines"""

    def __init__(self, lines: Text_Lines) -> None:
        self.lines: Text_Lines = lines

    def _fill_depth(self, headers: list[Header]) -> Text_Lines:
        """fill depth info into text lines. if a pattern hit in a line, then fill depth into the line."""
        for line in self.lines:
            for header in sorted(headers, key=lambda h: h.depth):
                if regex.search(header.pat, line.text) is not None:
                    line.depth = header.depth
                    break
        return self.lines

    def _fill_child_info(self, lines: Text_Lines) -> Text_Lines:
        """fill has_child info into text lines. has_child is true precisely when the line has successor who has no depth order or a deeper depth"""
        next_has_depth: bool = True
        next_depth: int = -1
        for line in reversed(lines):
            line.has_child = not next_has_depth or next_depth > line.depth
            next_has_depth = line.depth != -1
            next_depth = line.depth
        return lines

    def fill(self, headers: list[Header]) -> Text_Lines:
        lines = self._fill_depth(headers=headers)
        return self._fill_child_info(lines=lines)
