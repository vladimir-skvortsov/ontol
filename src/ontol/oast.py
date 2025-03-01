from enum import Enum
from typing import Optional
from dataclasses import dataclass, field


class ASTNode:
    pass


@dataclass
class Term(ASTNode):
    name: str
    label: str = ''
    description: str = ''
    attributes: dict = field(default_factory=dict)

    def __repr__(self) -> str:
        return f'Term(name={self.name}, label={self.label}, description={self.description}, attributes={self.attributes})'


@dataclass
class FunctionArgument(ASTNode):
    term: Term
    label: str = ''

    def __repr__(self) -> str:
        return f"('{self.term.name}', '{self.label}')"


@dataclass
class Function(ASTNode):
    name: str
    label: str
    input_types: list[FunctionArgument]
    output_type: FunctionArgument
    attributes: dict = field(default_factory=dict)

    def __repr__(self) -> str:
        return (
            f'Function(name={self.name}, label={self.label}, input_types={self.input_types},'
            f' output_type={self.output_type}, '
            f'attributes={self.attributes})'
        )

    def _format_input_types(self) -> str:
        return (
            '['
            + ', '.join(
                f'{{name: {t.term.name}, label: {t.label}}}' for t in self.input_types
            )
            + ']'
        )

    def _format_output_type(self) -> str:
        return (
            f'{{name: {self.output_type.term.name}, label: {self.output_type.label}}}'
        )


class RelationshipType(Enum):
    # TODO: change name by Novikov opinion
    DEPENDS = 'depends'
    ASSOCIATION = 'association'
    DIRECT_ASSOCIATION = 'directAssociation'
    INHERITANCE = 'inheritance'
    REALIZATION = 'realization'
    AGGREGATION = 'aggregation'
    COMPOSITION = 'composition'

    @classmethod
    def from_str(cls, value: str):
        return cls._value2member_map_.get(value, None)

    @classmethod
    def has_value(cls, value: str) -> bool:
        return value in cls._value2member_map_


@dataclass
class Relationship(ASTNode):
    parent: Term
    relationship: RelationshipType
    children: list[Term]
    attributes: dict[str, str] = field(default_factory=dict)

    def __repr__(self) -> str:
        return (
            f'Relationship(parent={self.parent.name}, '
            f'relationship={self.relationship.value}, '
            f'children=[{",".join(child.name for child in self.children)}], attributes={self.attributes})'
        )


@dataclass
class Meta(ASTNode):
    version: Optional[str] = None
    title: Optional[str] = None
    author: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    date: Optional[str] = None

    def __repr__(self) -> str:
        return (
            f'Meta(version={self.version}, title={self.title}, author={self.author}, '
            f'description={self.description}, type={self.type}, '
            f'date={self.date})'
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

    def find_term_by_name(self, name: str) -> Optional[Term]:
        return next((term for term in self.types if term.name == name), None)

    def find_function_by_name(self, name: str) -> Optional[Function]:
        return next(
            (function for function in self.functions if function.name == name), None
        )

    def __repr__(self) -> str:
        return (
            f'Ontology(types={self.types}, '
            f'functions={self.functions},'
            f'hierarchy={self.hierarchy},'
            f'meta={self.meta})'
        )
