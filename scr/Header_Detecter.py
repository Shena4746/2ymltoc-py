import dataclasses
from typing import Optional

import regex
from regex import Match, Pattern
from typing_extensions import Self

from Mediator import Mediator, Option
from Text_Lines import Text_Lines, Texts_Printer


@dataclasses.dataclass
class Header:
    pat: Pattern
    depth: int = 0
    idx: int = -1


@dataclasses.dataclass
class Header_Candidate:
    pat: Pattern
    appearance: int = 0
    sample: str = ""
    depth: int = 0

    @classmethod
    def to_header_candidates(cls, d: dict[Pattern, int]) -> list[Self]:
        return sorted(
            [Header_Candidate(pat=key, appearance=value) for key, value in d.items()],
            key=lambda form: form.appearance,
        )


class Header_Detecter:
    def __init__(
        self,
        lines: Text_Lines,
        digits: str = "ixv\\p{Nl}\\d",
        key_single: list[str] = ["part", "chapter", "section", "appendix"],
        key_paired: list[tuple[str, str]] = [],
        key_no_digit: list[str] = ["appendix", "preliminaries", "preliminary"],
        seps: list[str] = [".", "-"],
    ) -> None:
        self.mediator = Mediator(public_options=[Option.Exit.value], private_options=[Option.Digit.value])
        self.printer = Texts_Printer()
        self.lines: Text_Lines = lines
        self.digits: str = digits
        self.seps: list[str] = seps
        self.key_single: list[str] = key_single
        self.key_paired: list[tuple[str, str]] = key_paired
        self.key_no_digit: list[str] = key_no_digit
        self.header_patterns: list[Pattern] = (
            self._generate_single_patterns()
            + self._generate_paired_patterns()
            + self._generate_no_digit_patterns()
            + self._generate_multi_digit_patterns()
            + self._generate_mono_digit_patterns()
        )

    def _generate_header_raw_patterns(self) -> list[str]:
        return ["^", f"^[^{self.digits}\\s]" + "{1,3}"]

    def _generate_header_samples(self) -> list[str]:
        return ["" if raw_pat == "^" else "(Symbol)" for raw_pat in self._generate_header_raw_patterns()]

    def _generate_mono_digit_seps(self) -> list[str]:
        return list(set(self.seps + [""]))

    def _generate_single_patterns(self) -> list[Pattern]:
        return [regex.compile(f"^{key}\\s?[{self.digits}]", regex.IGNORECASE) for key in self.key_single]

    def _generate_paired_patterns(self) -> list[Pattern]:
        return [
            regex.compile(f"^{key1}\\s?[{self.digits}]+\\s?{key2}", regex.IGNORECASE) for key1, key2 in self.key_paired
        ]

    def _generate_no_digit_patterns(self) -> list[Pattern]:
        return [regex.compile(f"^\\S*?\\s?{key}", regex.IGNORECASE) for key in self.key_no_digit]

    def _generate_multi_digit_patterns(self) -> list[Pattern]:
        return [
            regex.compile(f"{header_raw_pat}[{self.digits}]+(?={regex.escape(sep)}[{self.digits}])")
            for sep in self.seps
            for header_raw_pat in self._generate_header_raw_patterns()
        ]

    def _generate_mono_digit_patterns(self) -> list[Pattern]:
        return [
            regex.compile(f"{header_raw_pat}[{self.digits}]+{regex.escape(sep)}(?=\\s)")
            for header_raw_pat in self._generate_header_raw_patterns()
            for sep in self._generate_mono_digit_seps()
        ]

    # these samples are used for display when the program asks user to choose patterns
    def _generate_multi_digit_samples(self) -> list[str]:
        seps: list[str] = [regex.escape(sep) for sep in self.seps]
        return [f"{sample}X{sep}Y{sep}Z" for sep in seps for sample in self._generate_header_samples()]

    def _generate_mono_digit_samples(self) -> list[str]:
        return [
            f"{sample}X{regex.escape(sep)}"
            for sample in self._generate_header_samples()
            for sep in self._generate_mono_digit_seps()
        ]

    def _generate_single_samples(self) -> list[str]:
        return [f"{key} X" for key in self.key_single]

    def _generate_paired_samples(self) -> list[str]:
        return [f"{key1} X {key2}" for key1, key2 in self.key_paired]

    def _generate_no_digit_samples(self) -> list[str]:
        return [f"{key}" for key in self.key_no_digit]

    def _generate_pat_sample_correspondence(self) -> dict[Pattern, str]:
        return dict(
            zip(
                self._generate_single_patterns()
                + self._generate_paired_patterns()
                + self._generate_no_digit_patterns()
                + self._generate_multi_digit_patterns()
                + self._generate_mono_digit_patterns(),
                self._generate_single_samples()
                + self._generate_paired_samples()
                + self._generate_no_digit_samples()
                + self._generate_multi_digit_samples()
                + self._generate_mono_digit_samples(),
            )
        )

    # def detect(self) -> None:
    #     self.Header_Candidate_freq = self._get_frequency()
    #     self.Header_Candidate = None if (sym := self.get_Header_Candidate()) is None else sym.form
    #     self.pat_leading_symbol = self._generate_patterns()

    def _get_frequency(self, patterns: list[Pattern]) -> dict[Pattern, int]:
        """get potential Header_Candidate header with their appearance times"""
        freq: dict[Pattern, int] = {}
        for line in self.lines:
            for pat in patterns:
                hit: Optional[Match] = regex.search(pat, line.text)
                if isinstance(hit, Match):
                    freq.setdefault(pat, 0)
                    freq[pat] += 1
        return freq

    def _show_headers(self, headers: list[Header_Candidate]) -> None:
        if len(headers) > 0:
            print("\n")
            for i, Header_Candidate in enumerate(headers):
                print(f"{i} | {Header_Candidate.sample}, appears {Header_Candidate.appearance} times")
            print("\n")
        else:
            print("no headers are detected.")

    def _choose_headers(self, candidates: list[Header_Candidate]) -> list[Header]:
        # end if freq is empty
        if len(candidates) == 0:
            return []
        headers: list[Header] = []
        self.mediator.explain()
        # choose from candidates, and assign it a depth
        # repeat until exit is chosen or candidate becomes zero
        depth_default: int = 0
        while True:
            if len(candidates) == 0:
                break
            # show candidates
            self._show_headers(headers=candidates)
            user_input, _ = self.mediator.get_user_input(default_value="0", domain=range(len(candidates)))
            choice = self.mediator.interpret(user_input=user_input)
            match choice.option:
                case Option.Exit:
                    break
                case Option.Digit:
                    header: Header_Candidate = candidates[choice.number]
                    depth: int = self._choose_depth(depth_max=len(candidates) + 1, default=str(depth_default))
                    if depth >= 0:
                        headers.append(Header(pat=header.pat, depth=depth))
                        candidates.pop(choice.number)
                    else:
                        break
                    depth_default = max(depth, depth_default) + 1 if depth >= depth_default else depth
                case _:
                    raise Exception(f"unknown choice type {choice.option}.")
        return headers

    def _choose_depth(self, depth_max: int, default: str = "0", msg: str = "enter depth") -> int:
        """ask user to enter depth for a chosen header. if exit is chosen, the caller should implement exit operation."""
        user_input, _ = self.mediator.get_user_input(msg=msg, default_value=default, domain=range(0, depth_max + 1))
        choice = self.mediator.interpret(user_input=user_input)
        match choice.option:
            case Option.Exit:
                return -1
            case Option.Digit:
                return choice.number
            case _:
                raise Exception(f"unknown choice type {choice.option}.")

    def _name_headers(self, headers: list[Header_Candidate]) -> list[Header_Candidate]:
        """fill sample property of a given list of headers."""
        corr: dict[Pattern, str] = self._generate_pat_sample_correspondence()
        return [
            Header_Candidate(pat=header.pat, appearance=header.appearance, sample=corr[header.pat])
            for header in headers
        ]

    def choose_headers(self) -> list[Header]:
        """interactively choose header and depth."""
        candidates: list[Header_Candidate] = Header_Candidate.to_header_candidates(
            self._get_frequency(patterns=self.header_patterns)
        )
        candidates = self._name_headers(headers=candidates)
        if len(candidates) > 0:
            print("choose header pattern and depth.")
            headers: list[Header] = self._choose_headers(candidates)
            return headers + self._choose_back_matter(headers=headers)
        return []

    def _find_last_block(self, headers: list[Header]) -> int:
        """search the oldest index of line that hits some header pattern.
        returns -1 if no rows are hit.
        """
        for line in reversed(self.lines):
            for header in headers:
                if regex.search(header.pat, line.text) is not None:
                    return line.idx
        return -1

    def _choose_head_of_back_matter(self, idx_last_block: int) -> int:
        """ask user where the back matter starts. return the positional idx in lines."""
        pos_idx: int = self.lines.search(row_idx=idx_last_block)
        length: int = len(self.lines[pos_idx:])
        # show possible back matter region and ask user where the head is.
        self.printer.print(lines=self.lines, start=pos_idx, with_page_idx=False)
        user_input, _ = self.mediator.get_user_input(
            msg="enter the head of back matter", default_value="0", domain=range(length + 1)
        )
        choice = self.mediator.interpret(user_input=user_input)
        match choice.option:
            case Option.Exit:
                return -1
            case Option.Digit:
                return choice.number + pos_idx
            case _:
                raise Exception(f"unknown choice type {choice.option}.")

    def _choose_back_matter(self, headers: list[Header]) -> list[Header]:
        """define the back matter region and assign it a depth."""
        idx_last_block: int = self._find_last_block(headers=headers)
        # there is nothing to do if no blocks are found
        if idx_last_block < 0:
            return []
        pos_idx: int = self._choose_head_of_back_matter(idx_last_block)
        # stop if pos_idx is -1 (exit)
        if pos_idx < 0:
            return []
        # use below if you need to interactively determine the depth of back matter.
        # --------------------------------------------
        # depth_max: int = max([header.depth for header in headers])
        # depth: int = self._choose_depth(depth_max=depth_max + 1, msg="enter depth for back matter.")
        # --------------------------------------------
        return [Header(pat=regex.compile(f"^{line.text}"), depth=0, idx=line.idx) for line in self.lines[pos_idx:]]
        # header.pat will not be used since header.idx identifies exactly where the depth should be applied.
        # the pat is provided just for understanding my intension and for error handling.


class Header_Detecter_ja(Header_Detecter):
    def __init__(
        self,
        lines: Text_Lines,
        digits: str = "ixv\\p{N}〇一二三四五六七八九十",
        key_single: list[str] = ["part", "chapter", "section", "appendix", "付録"],
        key_paired: list[tuple[str, str]] = [("第", "部"), ("第", "章"), ("第", "節")],
        key_no_digit: list[str] = ["appendix", "preliminaries", "preliminary", "付録"],
    ) -> None:
        super().__init__(lines, digits, key_single, key_paired, key_no_digit)
