from __future__ import annotations

from dataclasses import dataclass
from typing import List

from app.lexer.token import Token


KEYWORDS = {
    "OBTENER",
    "DE",
    "DONDE",
    "ORDENAR",
    "ASC",
    "DESC",
    "LIMITE",
    "Y",
    "O",
    "NO",
}


@dataclass
class LexError(Exception):
    message: str
    line: int
    column: int

    def __str__(self) -> str:
        return f"Léxico: {self.message} (línea {self.line}, columna {self.column})"


class Lexer:
    def __init__(self, text: str) -> None:
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []
        while self._current_char() is not None:
            char = self._current_char()
            if char in " \t\r":
                self._advance()
                continue
            if char == "\n":
                self._advance_line()
                continue
            if char.isalpha() or char == "_":
                tokens.append(self._read_identifier())
                continue
            if char.isdigit():
                tokens.append(self._read_number())
                continue
            if char in "'\"":
                tokens.append(self._read_string())
                continue

            if char == ",":
                tokens.append(self._make_token("COMMA", ","))
                self._advance()
                continue
            if char == "(":
                tokens.append(self._make_token("LPAREN", "("))
                self._advance()
                continue
            if char == ")":
                tokens.append(self._make_token("RPAREN", ")"))
                self._advance()
                continue
            if char == "*":
                tokens.append(self._make_token("STAR", "*"))
                self._advance()
                continue

            two = (char or "") + (self._peek() or "")
            if two in {">=", "<=", "!="}:
                tokens.append(self._make_token("OP", two))
                self._advance()
                self._advance()
                continue
            if char in {"=", ">", "<"}:
                tokens.append(self._make_token("OP", char))
                self._advance()
                continue

            raise LexError(f"Carácter inválido '{char}'", self.line, self.column)

        tokens.append(Token("EOF", None, self.line, self.column))
        return tokens

    def _current_char(self):
        if self.pos >= len(self.text):
            return None
        return self.text[self.pos]

    def _peek(self):
        if self.pos + 1 >= len(self.text):
            return None
        return self.text[self.pos + 1]

    def _advance(self) -> None:
        if self.pos < len(self.text):
            self.pos += 1
            self.column += 1

    def _advance_line(self) -> None:
        self.pos += 1
        self.line += 1
        self.column = 1

    def _make_token(self, token_type: str, value):
        return Token(token_type, value, self.line, self.column)

    def _read_identifier(self) -> Token:
        start_line = self.line
        start_col = self.column
        start = self.pos
        while self._current_char() is not None and (
            self._current_char().isalnum() or self._current_char() == "_"
        ):
            self._advance()
        value = self.text[start:self.pos]
        upper = value.upper()
        if upper in KEYWORDS:
            return Token(upper, upper, start_line, start_col)
        return Token("IDENT", value, start_line, start_col)

    def _read_number(self) -> Token:
        start_line = self.line
        start_col = self.column
        start = self.pos
        has_dot = False
        while self._current_char() is not None and (
            self._current_char().isdigit() or self._current_char() == "."
        ):
            if self._current_char() == ".":
                if has_dot:
                    break
                has_dot = True
            self._advance()
        value = self.text[start:self.pos]
        number = float(value) if has_dot else int(value)
        return Token("NUMBER", number, start_line, start_col)

    def _read_string(self) -> Token:
        quote = self._current_char()
        start_line = self.line
        start_col = self.column
        self._advance()
        start = self.pos
        while self._current_char() is not None and self._current_char() != quote:
            if self._current_char() == "\n":
                raise LexError("Cadena sin cerrar", start_line, start_col)
            self._advance()
        if self._current_char() != quote:
            raise LexError("Cadena sin cerrar", start_line, start_col)
        value = self.text[start:self.pos]
        self._advance()
        return Token("STRING", value, start_line, start_col)
