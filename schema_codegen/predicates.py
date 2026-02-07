import libcst as cst
import libcst.matchers as m
from libcst import BaseStatement


def is_docstring_stmt(stmt: BaseStatement) -> bool:
    return m.matches(
        stmt,
        m.SimpleStatementLine(
            body=[m.Expr(value=m.SimpleString() | m.ConcatenatedString())]
        ),
    )


def is_dataclass_class(class_node: cst.ClassDef) -> bool:
    for decorator in class_node.decorators:
        d = decorator.decorator
        if isinstance(d, cst.Name) and d.value == "dataclass":
            return True
        if isinstance(d, cst.Call) and isinstance(d.func, cst.Name) and d.func.value == "dataclass":
            return True
    return False


def is_import_statement(stmt: BaseStatement) -> bool:
    if not isinstance(stmt, cst.SimpleStatementLine):
        return False
    for small_stmt in stmt.body:
        if isinstance(small_stmt, cst.Import) or isinstance(small_stmt, cst.ImportFrom):
            return True
    return False
