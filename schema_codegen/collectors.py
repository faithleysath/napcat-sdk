import libcst as cst


class ClassCollector(cst.CSTVisitor):
    def __init__(self) -> None:
        self.definitions: dict[str, cst.ClassDef] = {}

    def visit_ClassDef(self, node: cst.ClassDef) -> None:
        self.definitions[node.name.value] = node


class NameCollector(cst.CSTVisitor):
    def __init__(self) -> None:
        self.names: set[str] = set()

    def visit_Name(self, node: cst.Name) -> None:
        self.names.add(node.value)
