from typing import Optional, Dict
from dataclasses import dataclass, field


class ASTNode:
    pass


@dataclass
class Term(ASTNode):
    name: str
    label: str
    description: str
    attributes: dict = field(default_factory=dict)

    def __repr__(self) -> str:
        return f'Term(name={self.name}, label={self.label}, description={self.description}, attributes={self.attributes})'


@dataclass
class Function(ASTNode):
    name: str
    label: str
    # TODO: replace tuple[str, str] with list[{ name: str, label: str }]
    # TODO: replace str with Term
    input_types: list[tuple[str, str]]
    # TODO: replace tuple[str, str] with dict { name: str, label: str }
    # TODO: replace str with Term
    output_type: tuple[str, str]
    attributes: dict = field(default_factory=dict)

    def __repr__(self) -> str:
        return (
            f'Function(name={self.name}, label={self.label}, input_types={self.input_types},'
            f' output_type={self.output_type}, '
            f'attributes={self.attributes})'
        )


# TODO: implement structure from technical task. Must contain parent, child, and relationship type
@dataclass
class Relationship(ASTNode):
    # TODO: replace str with Term
    parent: str
    # TODO: replace str with enum type
    relationship: str
    # TODO: replace str with Term
    child: list[str]
    attributes: Dict[str, str] = field(default_factory=dict)

    def __repr__(self) -> str:
        return (
            f'Relationship(parent={self.parent}, '
            f'relationship={self.relationship}, '
            f'child={self.child}, attributes={self.attributes})'
        )


@dataclass
class Meta(ASTNode):
    version: Optional[str] = None
    name: Optional[str] = None
    author: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    date_created: Optional[str] = None

    def __repr__(self) -> str:
        return (
            f'Meta(version={self.version}, name={self.name}, author={self.author}, '
            f'description={self.description}, type={self.type}, '
            f'date_created={self.date_created})'
        )


@dataclass
class Ontology(ASTNode):
    types: list[Term] = field(default_factory=list)
    functions: list[Function] = field(default_factory=list)
    hierarchy: list[Relationship] = field(default_factory=list)
    meta: Meta = field(default_factory=Meta)

    def add_type(self, type_def: Term) -> None:
        self.types.append(type_def)

    def add_function(self, func_def: Function) -> None:
        self.functions.append(func_def)

    def add_relationship(self, logical_expr: Relationship) -> None:
        self.hierarchy.append(logical_expr)

    def set_meta(self, meta: Meta) -> None:
        self.meta = meta

    def __repr__(self) -> str:
        return (
            f'Ontology(types={self.types}, '
            f'functions={self.functions},'
            f'hierarchy={self.hierarchy},'
            f'meta={self.meta})'
        )
