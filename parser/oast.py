from typing import Optional
from dataclasses import dataclass, field


class ASTNode:
    pass


@dataclass
class Term(ASTNode):
    name: str
    description: Optional[str] = None

    def __repr__(self) -> str:
        return f'Term(name={self.name}, description={self.description})'


@dataclass
class Function(ASTNode):
    name: str
    input_types: list[str] = field(default_factory=list)
    output_types: list[str] = field(default_factory=list)
    label: Optional[str] = None
    description: Optional[str] = None

    def __repr__(self) -> str:
        return f'Function(name={self.name}, input_types={self.input_types}, output_types={self.output_types}, label={self.label}, description={self.description})'


# TODO: implmenent structure from technical task. Must contain parent, child, and relationship type
@dataclass
class Relationship(ASTNode):
    expression: str

    def __repr__(self) -> str:
        return f'Relationship(expression={self.expression})'


@dataclass
class Meta(ASTNode):
    version: Optional[str]
    name: Optional[str]
    author: Optional[str]
    description: Optional[str]
    date_created: Optional[str]

    def __repr__(self) -> str:
        return (
            f'Meta(version={self.version}, name={self.name}, author={self.author}, '
            f'description={self.description}, date_created={self.date_created})'
        )


@dataclass
class Ontology(ASTNode):
    types: list[Term] = field(default_factory=list)
    functions: list[Function] = field(default_factory=list)
    hierarchy: list[Relationship] = field(default_factory=list)
    meta: Optional[Meta] = None

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
            f'hierarchy={self.hierarchy},'
            f'meta={self.meta})'
        )
