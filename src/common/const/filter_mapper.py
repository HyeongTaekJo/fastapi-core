from sqlalchemy import and_, or_
from sqlalchemy.sql import operators, expression
from sqlalchemy import func
from sqlalchemy.sql import not_

from sqlalchemy import (
    not_, or_, and_, null, asc, desc, literal, text,
    between, func,
)
from sqlalchemy.sql import operators
from sqlalchemy.sql.elements import BinaryExpression
from sqlalchemy import (
    Column, String, Integer, Float, Boolean,
    DateTime
)

from sqlalchemy import (
    not_,
    or_,
    and_,
    null,
    asc,
    desc,
    between,
    func,
    text,
    literal
)
from sqlalchemy.sql import operators
from sqlalchemy.sql.elements import BinaryExpression
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime

from sqlalchemy import (
    Column, and_, or_, not_,
    between, func,
    select
)
from sqlalchemy.sql import operators
from sqlalchemy.sql.expression import literal

from sqlalchemy import (
    Column, and_, or_, not_,
    between, func,
    select,
    asc, desc, text,
    literal
)

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime,
    and_, or_, not_,
    between, func,
    select,
    asc, desc,
    text, literal
)
from sqlalchemy.sql.elements import BinaryExpression

from sqlalchemy import (
    Column,
    and_,
    or_,
    not_,
    between,
    func,
    asc,
    desc,
    text,
    literal
)
from sqlalchemy.sql.elements import BinaryExpression

FILTER_MAPPER = {
    "not": lambda col, v: not_(col == v),
    "more_than": lambda col, v: col > v,
    "less_than": lambda col, v: col < v,
    "less_than_or_equal": lambda col, v: col <= v,
    "greater_than": lambda col, v: col > v,
    "greater_than_or_equal": lambda col, v: col >= v,
    "equal": lambda col, v: col == v,
    "like": lambda col, v: col.like(f"%{v}%"),
    "i_like": lambda col, v: col.ilike(f"%{v}%"),
    "in": lambda col, v: col.in_(v if isinstance(v, list) else v.split(",")),
    "between": lambda col, v: col.between(*v.split(",")),
    "is_null": lambda col, v: col.is_(None) if v else col.is_not(None),
}
