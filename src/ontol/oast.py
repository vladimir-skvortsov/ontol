import copy
from enum import Enum
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class Meta:
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

    def with_new_name(self, new_name: str) -> 'Meta':
        return Meta(
            version=self.version,
            title=new_name,
            author=self.author,
            description=self.description,
            type=self.type,
            date=self.date,
        )


@dataclass
class TermAttributes:
    color: Optional[str] = None
    note: Optional[str] = None

    def __repr__(self) -> str:
        return f'TermAttributes(color={self.color}, note={self.note})'


@dataclass
class Term:
    name: str
    label: str = ''
    description: str = ''
    attributes: TermAttributes = field(default_factory=TermAttributes)

    def __repr__(self) -> str:
        return f'Term(name={self.name}, label={self.label}, description={self.description}, attributes={self.attributes})'


class RelationshipDirection(Enum):
    FORWARD = 'forward'
    BACKWARD = 'backward'
    BIDIRECTIONAL = 'bidirectional'

    @classmethod
    def from_str(cls, value: str):
        return cls._value2member_map_.get(value, None)

    @classmethod
    def has_value(cls, value: str) -> bool:
        return value in cls._value2member_map_


class RelationshipType(Enum):
    # TODO: change name by Novikov opinion
    DEPENDENCE = 'dependence'
    ASSOCIATION = 'association'
    DIRECT_ASSOCIATION = 'directAssociation'
    INHERITANCE = 'inheritance'
    IMPLEMENTATION = 'implementation'
    AGGREGATION = 'aggregation'
    COMPOSITION = 'composition'

    @classmethod
    def from_str(cls, value: str) -> Optional['RelationshipType']:
        return cls._value2member_map_.get(value, None)

    @classmethod
    def has_value(cls, value: str) -> bool:
        return value in cls._value2member_map_


@dataclass
class FunctionAttributes:
    color: Optional[str] = None
    colorArrow: Optional[str] = None
    type: Optional[RelationshipType] = None
    inputTitle: Optional[str] = None
    outputTitle: Optional[str] = None

    def __repr__(self) -> str:
        return (
            f'FunctionAttributes(color={self.color}, '
            f'colorArrow={self.colorArrow}, '
            f'type={self.type.value if self.type else self.type}, '
            f'inputTitle={self.inputTitle}, '
            f'outputTitle={self.outputTitle})'
        )


@dataclass
class FunctionArgument:
    term: Term
    label: str = ''

    def __repr__(self) -> str:
        return f"('{self.term.name}', '{self.label}')"


@dataclass
class Function:
    name: str
    label: str
    input_types: list[FunctionArgument]
    output_type: FunctionArgument
    attributes: FunctionAttributes = field(default_factory=FunctionAttributes)

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


@dataclass
class RelationshipAttributes:
    color: Optional[str] = None
    direction: Optional[RelationshipDirection] = None
    title: Optional[str] = None
    rightChar: Optional[str] = None
    leftChar: Optional[str] = None

    def __repr__(self) -> str:
        return (
            f'RelationshipAttributes(color={self.color}, '
            f'direction={self.direction.value if self.direction else self.direction}, '
            f'title={self.title}, '
            f'rightChar={self.rightChar}, '
            f'leftChar={self.leftChar})'
        )


@dataclass
class Relationship:
    parent: Term
    relationship: RelationshipType
    children: list[Term]
    name: Optional[str] = None
    attributes: RelationshipAttributes = field(default_factory=RelationshipAttributes)

    def __repr__(self) -> str:
        return (
            f'Relationship(parent={self.parent.name}, '
            f'relationship={self.relationship.value}, '
            f'children=[{",".join(child.name for child in self.children)}], attributes={self.attributes})'
        )


@dataclass
class Figure:
    name: str
    types: list[Term] = field(default_factory=list)
    functions: list[Function] = field(default_factory=list)
    hierarchy: list[Relationship] = field(default_factory=list)

    def __repr__(self) -> str:
        return f'Figure(name={self.name}, tyoes={self.types}, functions={self.functions}, hierarchy={self.hierarchy})'


@dataclass
class Ontology:
    meta: Meta = field(default_factory=Meta)
    types: list[Term] = field(default_factory=list)
    functions: list[Function] = field(default_factory=list)
    hierarchy: list[Relationship] = field(default_factory=list)
    figures: list[Figure] = field(default_factory=list)

    @staticmethod
    def from_figure(parent_ontology: 'Ontology', figure: Figure) -> 'Ontology':
        return Ontology(
            meta=copy.copy(parent_ontology.meta),
            types=figure.types,
            functions=figure.functions,
            hierarchy=figure.hierarchy,
        )

    def add_type(self, type_def: Term) -> None:
        self.types.append(type_def)

    def add_function(self, func_def: Function) -> None:
        self.functions.append(func_def)

    def add_relationship(self, relationship: Relationship) -> None:
        self.hierarchy.append(relationship)

    def add_figure(self, figure: Figure) -> None:
        self.figures.append(figure)

    def set_meta(self, meta: Meta) -> None:
        self.meta = meta

    def find_term_by_name(self, name: str) -> Optional[Term]:
        return next((term for term in self.types if term.name == name), None)

    def find_function_by_name(self, name: str) -> Optional[Function]:
        return next(
            (function for function in self.functions if function.name == name), None
        )

    def find_relationship_by_name(self, name: str) -> Optional[Relationship]:
        return next(
            (
                relationship
                for relationship in self.hierarchy
                if relationship.name == name
            ),
            None,
        )

    def find_definition_by_name(
        self, name: str
    ) -> Optional[Term | Function | Relationship]:
        definitions: list[Term | Function | Relationship] = (
            self.types + self.functions + self.hierarchy
        )
        return next(
            (definition for definition in definitions if definition.name == name),
            None,
        )

    @property
    def without_functions(self) -> 'Ontology':
        types_used_in_hierarchy = [
            term
            for relationship in self.hierarchy
            for term in [relationship.parent] + relationship.children
        ]
        return Ontology(
            meta=self.meta.with_new_name(f'{self.meta.title} | Иерархия'),
            types=types_used_in_hierarchy,
            functions=[],
            hierarchy=self.hierarchy,
            figures=self.figures,
        )

    @property
    def only_functions(self) -> 'Ontology':
        types_used_in_functions = [
            arg.term
            for func in self.functions
            for arg in func.input_types + [func.output_type]
        ]
        return Ontology(
            meta=self.meta.with_new_name(f'{self.meta.title} | Алгоритмы'),
            types=types_used_in_functions,
            functions=self.functions,
            hierarchy=[],
            figures=self.figures,
        )

    def __repr__(self) -> str:
        return (
            f'Ontology(meta={self.meta}, '
            f'types={self.types}, '
            f'functions={self.functions}, '
            f'hierarchy={self.hierarchy}, '
            f'figures={self.figures})'
        )

    def count_edges(self) -> int:
        count: int = len(self.hierarchy)
        for func in self.functions:
            types: list[str] = [attribute.term.name for attribute in func.input_types]
            count += len(set(types)) + 1
        return count
