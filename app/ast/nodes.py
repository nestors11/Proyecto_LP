from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Union


@dataclass
class Identifier:
    name: str


@dataclass
class Literal:
    value: Union[str, int, float, bool, None]


@dataclass
class BinaryExpression:
    left: Expression
    operator: str
    right: Expression


@dataclass
class UnaryExpression:
    operator: str
    operand: Expression


@dataclass
class OrderClause:
    field: Identifier
    direction: str


@dataclass
class SelectQuery:
    fields: List[Identifier] | None
    source: Identifier
    where: Optional[Expression]
    order_by: Optional[OrderClause]
    limit: Optional[int]


Expression = Union[BinaryExpression, UnaryExpression, Identifier, Literal]
