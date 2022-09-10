import regex
from regex import Pattern

from Text_Line import Text_Line
from Text_Lines import Text_Lines, _Text_Lines


class Formatter:
    """convert text lines with header info into a yaml file suitable for pdftoc tool."""

    def __init__(self, lines: Text_Lines, indentation_by_space: bool = True, indentation_amount: int = 2) -> None:
        self.lines = lines
        self.indent: str = (" " if indentation_by_space else "\\t") * indentation_amount

    def _insert_blank_line(self) -> Text_Lines:
        """insert a blank line after lines with non-trivial depth and child."""
        lines: list[Text_Line] = []
        # double idx of lines in order to insert blank line without disturbing increasing order of idx
        # this makes idx comparison impossible between new lines and old ones.
        for line in self.lines.change_idx(fn=lambda line: line.idx * 2):
            lines.append(line)
            if line.is_depth_set() and line.has_child:
                lines.append(Text_Line(text="", idx=line.idx + 1, sep=line.sep, depth=line.depth))
        return Text_Lines(lines)

    def _place_hyphen(self, lines: Text_Lines) -> Text_Lines:
        """place hyphen at the beginning of each line. this method should be called after blank lines are appropriately inserted."""
        hyphen: str = "- "
        for line in lines:
            line.text = hyphen + line.text
        return lines

    def _apply_indentation(self, lines: Text_Lines) -> Text_Lines:
        """give each line appropriate amount of indentation. the amount is calculated by header information in textline; depth and has_child."""
        # initial value -1 is convenient to set front matter depth = 0
        last_depth: int = -1
        for line in lines:
            if line.is_depth_set():
                line = self._add_indentation(line=line, size=line.depth)
                last_depth = line.depth
            else:
                line = self._add_indentation(line=line, size=last_depth + 1)
        return lines

    def _add_indentation(self, line: Text_Line, size: int) -> Text_Line:
        """apply specified size indentation at line.text."""
        line.text = self.indent * size + line.text
        return line

    def _add_tail_new_line(self, lines: Text_Lines) -> Text_Lines:
        idx_largest: int = max([line.idx for line in lines])
        return lines + Text_Lines([Text_Line(text="", idx=idx_largest + 1)])

    def _kill_map_exp(self, lines: Text_Lines) -> Text_Lines:
        """kill yaml map expressions."""
        pat_colon: Pattern = regex.compile(":+\\s+")
        # delete trailing colons
        pat_trailing_colon: Pattern = regex.compile(":+\\s*(?P<page>\\d+)$")
        for line in lines:
            line.text = regex.sub(pat_trailing_colon, lambda m: f" {m.group('page')}", line.text)
            line.text = regex.sub(pat_colon, ":", line.text)
        return lines

    def _move_leading_asterisk(self, lines: Text_Lines) -> Text_Lines:
        pat: Pattern = regex.compile("^\\*(\\S+)")
        for line in lines:
            line.text = regex.sub(pat, "\\1*", line.text)
        return lines

    def format(self) -> _Text_Lines:
        lines = self._insert_blank_line()
        lines = self._move_leading_asterisk(lines)
        lines = self._kill_map_exp(lines)
        lines = self._place_hyphen(lines)
        lines = self._apply_indentation(lines)
        return self._add_tail_new_line(lines)
