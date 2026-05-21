from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from app.ast.nodes import (
    BinaryExpression,
    Identifier,
    Literal,
    OrderClause,
    SelectQuery,
    UnaryExpression,
    Expression,
)
from app.lexer.lexer import Lexer
from app.lexer.token import Token


@dataclass
class ParseError(Exception):
    message: str
    line: int
    column: int

    def __str__(self) -> str:
        return f"Sintaxis: {self.message} (línea {self.line}, columna {self.column})"


class Parser:
    def __init__(self, text: str) -> None:
        self.tokens = Lexer(text).tokenize()
        self.pos = 0

    def parse(self) -> SelectQuery:
        query = self._parse_query()
        self._expect("EOF")
        return query

    def _current(self) -> Token:
        return self.tokens[self.pos]

    def _advance(self) -> Token:
        token = self._current()
        self.pos += 1
        return token

    def _expect(self, token_type: str) -> Token:
        token = self._current()
        if token.type != token_type:
            raise ParseError(
                f"Se esperaba {token_type} y se encontró {token.type}",
                token.line,
                token.column,
            )
        return self._advance()

    def _match(self, token_type: str) -> Optional[Token]:
        if self._current().type == token_type:
            return self._advance()
        return None

    def _parse_query(self) -> SelectQuery:
        self._expect("OBTENER")
        fields = self._parse_fields()
        self._expect("DE")
        source = self._parse_identifier()

        where_expr: Optional[Expression] = None
        order_by: Optional[OrderClause] = None
        limit: Optional[int] = None

        if self._match("DONDE"):
            where_expr = self._parse_expression()

        if self._match("ORDENAR"):
            order_by = self._parse_order_clause()

        if self._match("LIMITE"):
            limit = self._parse_limit()

        return SelectQuery(fields, source, where_expr, order_by, limit)

    def _parse_fields(self):
        if self._match("STAR"):
            return None
        fields = [self._parse_identifier()]
        while self._match("COMMA"):
            fields.append(self._parse_identifier())
        return fields

    def _parse_identifier(self) -> Identifier:
        token = self._expect("IDENT")
        return Identifier(token.value)

    def _parse_order_clause(self) -> OrderClause:
        field = self._parse_identifier()
        direction = "ASC"
        if self._match("ASC"):
            direction = "ASC"
        elif self._match("DESC"):
            direction = "DESC"
        return OrderClause(field, direction)

    def _parse_limit(self) -> int:
        token = self._expect("NUMBER")
        if not isinstance(token.value, int):
            raise ParseError("LIMITE debe ser un entero", token.line, token.column)
        return token.value

    def _parse_expression(self) -> Expression:
        return self._parse_or()

    def _parse_or(self) -> Expression:
        expr = self._parse_and()
        while self._match("O"):
            right = self._parse_and()
            expr = BinaryExpression(expr, "O", right)
        return expr

    def _parse_and(self) -> Expression:
        expr = self._parse_not()
        while self._match("Y"):
            right = self._parse_not()
            expr = BinaryExpression(expr, "Y", right)
        return expr

    def _parse_not(self) -> Expression:
        if self._match("NO"):
            operand = self._parse_not()
            return UnaryExpression("NO", operand)
        return self._parse_comparison()

    def _parse_comparison(self) -> Expression:
        left = self._parse_term()
        if self._current().type == "OP":
            op = self._advance().value
            right = self._parse_term()
            return BinaryExpression(left, op, right)
        return left

    def _parse_term(self) -> Expression:
        current = self._current()
        if self._match("LPAREN"):
            expr = self._parse_expression()
            self._expect("RPAREN")
            return expr
        if current.type == "IDENT":
            return self._parse_identifier()
        if current.type == "NUMBER":
            token = self._advance()
            return Literal(token.value)
        if current.type == "STRING":
            token = self._advance()
            return Literal(token.value)
        raise ParseError(
            f"Token inesperado {current.type}", current.line, current.column
        )
