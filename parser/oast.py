from typing import Optional


class ASTNode:
    pass


class Term(ASTNode):
    def __init__(self, name: str, description: Optional[str] = None) -> None:
        self.name = name
        self.description = description

    def __repr__(self) -> str:
        return f'Term(name={self.name}, description={self.description})'


class Function(ASTNode):
    def __init__(
        self,
        name: str,
        input_types: list[str],
        output_types: list[str],
        label: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None:
        self.name = name
        self.input_types = input_types
        self.output_types = output_types
        self.label = label
        self.description = description

    def __repr__(self) -> str:
        return f'Function(name={self.name}, input_types={self.input_types}, output_types={self.output_types}, label={self.label}, description={self.description})'


class Relationship(ASTNode):
    def __init__(self, expression: str) -> None:
        self.expression = expression

    def __repr__(self) -> str:
        return f'Relationship(expression={self.expression})'


class Meta(ASTNode):
    def __init__(
        self,
        version: Optional[str],
        name: Optional[str],
        author: Optional[str],
        description: Optional[str],
        date_created: Optional[str],
    ) -> None:
        self.version = version
        self.name = name
        self.author = author
        self.description = description
        self.date_created = date_created

    def __repr__(self) -> str:
        return (
            f'Meta(version={self.version}, name={self.name}, author={self.author}, '
            f'description={self.description}, date_created={self.date_created})'
        )


class Ontology(ASTNode):
    def __init__(self) -> None:
        self.types: list[Term] = []
        self.functions: list[Function] = []
        self.hierarchy: list[Relationship] = []
        self.meta: Optional[Meta] = None

    def add_type(self, type_def: Term) -> None:
        self.types.append(type_def)

    def add_function(self, func_def: Function) -> None:
        self.functions.append(func_def)

    def add_relationship(self, logical_expr: Relationship) -> None:
        self.hierarchy.append(logical_expr)

    def set_meta(self, meta: Meta) -> None:
        if self.meta is not None:
            raise ValueError(
                'Meta information is already set and can only be set once.'
            )
        self.meta = meta

    def __repr__(self) -> str:
        return (
            f'Ontology(types={self.types}, '
            f'functions={self.functions},'
            f'hierarchy={self.hierarchy}'
        )
