import json
from dataclasses import fields
from typing import Union

from ontol import (
    Function,
    Ontology,
    Relationship,
    Term,
    RelationshipAttributes,
    TermAttributes,
    FunctionAttributes,
)


class Retranslator:
    def translate(self, ontology: Ontology) -> str:
        ontol_lines: list[str] = []

        for field in fields(ontology.meta):
            value = getattr(ontology.meta, field.name)
            if value is not None:
                ontol_lines.append(f'{field.name}: {value!r}')
        ontol_lines.append('')

        if ontology.types:
            ontol_lines.append('types:')
            for term in ontology.types:
                ontol_lines.append(self.__translate_term(term))
            ontol_lines.append('')

        if ontology.functions:
            ontol_lines.append('functions:')
            for function in ontology.functions:
                ontol_lines.append(self.__translate_function(function))
            ontol_lines.append('')

        if ontology.hierarchy:
            ontol_lines.append('hierarchy:')
            for relationship in ontology.hierarchy:
                ontol_lines.append(self.__translate_hierarchy(relationship))
            ontol_lines.append('')

        if ontology.figures:
            for figure in ontology.figures:
                ontol_lines.append(f'figure {figure.name}:')
                for definition in figure.types + figure.functions + figure.hierarchy:
                    if definition.name is not None:
                        ontol_lines.append(definition.name)
                ontol_lines.append('')

        return '\n'.join(ontol_lines)

    def __translate_term(self, term: Term) -> str:
        label = "'" + term.label + "'"
        term_line = f'{term.name}: {label}, {term.description!r}'

        return term_line + self.__translate_attributes(term.attributes)

    def __translate_function(self, function: Function) -> str:
        label = "'" + function.label + "'"
        function_line = f'{function.name}: {label} ('
        args = ''
        for i, arg in enumerate(function.input_types):
            args += f'{arg.term.name}: {arg.label!r}'
            if i < len(function.input_types) - 1:
                args += ', '
        function_line += (
            f'{args}) -> '
            f'{function.output_type.term.name}: {function.output_type.label!r}'
        )

        return function_line + self.__translate_attributes(function.attributes)

    def __translate_hierarchy(self, relationship: Relationship) -> str:
        relationship_line = (
            f'{relationship.parent.name} '
            f'{relationship.relationship.value} '
            f'{relationship.children[0].name}'
        )

        return relationship_line + self.__translate_attributes(relationship.attributes)

    def __translate_attributes(
        self,
        attributes: Union[RelationshipAttributes, FunctionAttributes, TermAttributes],
    ) -> str:
        res, non_none_fields = '', []
        for field in fields(attributes):
            if (attr := getattr(attributes, field.name)) is not None:
                if isinstance(attr, str):
                    attribute = attr
                else:
                    attribute = attr.value
                non_none_fields.append(f'{field.name}: {attribute!r} ')

        if non_none_fields:
            res += ', { ' + ', '.join(non_none_fields) + '}'

        return res
