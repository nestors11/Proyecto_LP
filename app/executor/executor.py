from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import pandas as pd

from app.ast.nodes import (
    BinaryExpression,
    Identifier,
    Literal,
    SelectQuery,
    UnaryExpression,
    Expression,
)


@dataclass
class ExecutionError(Exception):
    message: str

    def __str__(self) -> str:
        return f"Ejecución: {self.message}"


class QueryExecutor:
    def __init__(self, sources: Dict[str, pd.DataFrame]) -> None:
        self.sources = sources

    def execute(self, query: SelectQuery) -> pd.DataFrame:
        df = self.sources[query.source.name]

        if query.where:
            mask = self._eval_expression(query.where, df)
            try:
                df = df[mask]
            except Exception as exc:  # pragma: no cover - seguridad
                raise ExecutionError("Error al aplicar DONDE") from exc

        if query.fields is not None:
            columns = [field.name for field in query.fields]
            df = df[columns]

        if query.order_by:
            ascending = query.order_by.direction == "ASC"
            df = df.sort_values(by=query.order_by.field.name, ascending=ascending)

        if query.limit is not None:
            df = df.head(query.limit)

        return df

    def _eval_expression(self, expr: Expression, df: pd.DataFrame):
        if isinstance(expr, Identifier):
            return df[expr.name]
        if isinstance(expr, Literal):
            return expr.value
        if isinstance(expr, UnaryExpression):
            if expr.operator == "NO":
                value = self._eval_expression(expr.operand, df)
                return ~value
            raise ExecutionError(f"Operador no soportado {expr.operator}")
        if isinstance(expr, BinaryExpression):
            left = self._eval_expression(expr.left, df)
            right = self._eval_expression(expr.right, df)
            op = expr.operator
            if op == "=":
                return left == right
            if op == "!=":
                return left != right
            if op == ">":
                return left > right
            if op == "<":
                return left < right
            if op == ">=":
                return left >= right
            if op == "<=":
                return left <= right
            if op == "Y":
                return left & right
            if op == "O":
                return left | right
            raise ExecutionError(f"Operador no soportado {op}")
        raise ExecutionError("Expresión no soportada")
