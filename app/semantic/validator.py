from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import pandas as pd

from app.ast.nodes import (
    BinaryExpression,
    Identifier,
    SelectQuery,
    UnaryExpression,
    Literal,
    Expression,
)


@dataclass
class SemanticError(Exception):
    message: str

    def __str__(self) -> str:
        return f"Semántica: {self.message}"


class SemanticValidator:
    def __init__(self, sources: Dict[str, pd.DataFrame]) -> None:
        self.sources = sources

    def validate(self, query: SelectQuery) -> None:
        source_name = query.source.name
        if source_name not in self.sources:
            raise SemanticError(f"Fuente '{source_name}' no cargada")

        df = self.sources[source_name]
        columns = set(df.columns.astype(str))

        if query.fields is not None:
            for field in query.fields:
                if field.name not in columns:
                    raise SemanticError(
                        f"Columna '{field.name}' no existe en '{source_name}'"
                    )

        if query.order_by:
            if query.order_by.field.name not in columns:
                raise SemanticError(
                    f"Columna '{query.order_by.field.name}' no existe en '{source_name}'"
                )

        if query.where:
            self._validate_expression(query.where, columns)

    def _validate_expression(self, expr: Expression, columns: set[str]) -> None:
        if isinstance(expr, Identifier):
            if expr.name not in columns:
                raise SemanticError(f"Columna '{expr.name}' no existe")
            return
        if isinstance(expr, Literal):
            return
        if isinstance(expr, UnaryExpression):
            self._validate_expression(expr.operand, columns)
            return
        if isinstance(expr, BinaryExpression):
            self._validate_expression(expr.left, columns)
            self._validate_expression(expr.right, columns)
            return
