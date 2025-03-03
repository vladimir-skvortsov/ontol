import collections
import os
import zlib

import requests

from ontol import (
    Function,
    Ontology,
    Relationship,
    Term,
    RelationshipDirection,
    RelationshipType,
    RelationshipAttrubutes,
    TermAttributes,
    FunctionAttributes
)


# TODO: make look like in technical task
class PlantUML:
    SERVER_URL: str = 'http://www.plantuml.com/plantuml/img/'

    def __init__(self, url=SERVER_URL):
        self.url = url

    def generate(self, ontology: Ontology) -> str:
        if ontology.meta.type == 'Базовый' or ontology.meta.type is None:
            return self._generate_base(ontology)

    # def _generate_base(self, ontology: Ontology) -> str:
    #     uml_lines: list[str] = ['@startuml', 'skinparam classAttributeIconSize 0']
    #
    #     if ontology.meta:
    #         uml_lines.append(f'title {ontology.meta.title} by {ontology.meta.author}')
    #
    #     for term in ontology.types:
    #         uml_lines.append(self._generate_type(term))
    #
    #     for function in ontology.functions:
    #         uml_lines.append(self._generate_function(function))
    #
    #     for relationship in ontology.hierarchy:
    #         uml_lines.append(self._generate_relationship(relationship))
    #
    #     uml_lines.append('@enduml')
    #     return '\n'.join(uml_lines)

    def _generate_base(self, ontology: Ontology) -> str:
        uml_lines: list[str] = [
            '@startuml',
            'skinparam backgroundColor #F0F8FF',
            'skinparam defaultTextAlignment center',
            'skinparam shadowing false',
            'skinparam dpi 150',
            'skinparam linetype ortho',
            'skinparam ranksep 40',
            'skinparam nodesep 30',
            f'package "'
            f'{ontology.meta.title if ontology.meta.title is not None else "Онтология"}'
            f'" {{',
        ]

        for term in ontology.types:
            uml_lines.append(self._generate_rectangle(term))
            uml_lines.append(self._generate_note(term))

        for function in ontology.functions:
            uml_lines.append(
                self._generate_rectangle(self.__prepare_function_term(function))
            )

        for function in ontology.functions:
            for relations in self.__prepare_function_hierarchy(function, ontology):
                uml_lines.append(self._generate_base_hierarchy(relations))

        for relationship in ontology.hierarchy:
            uml_lines.append(self._generate_base_hierarchy(relationship))

        uml_lines.append('}')
        uml_lines.append('@enduml')
        return '\n'.join(uml_lines)

    @staticmethod
    def _generate_rectangle(term: Term) -> str:
        return (
            f'rectangle "{term.label}'
            + (f'\\n({term.description})' if term.description else '')
            + f'" as {term.name} {term.attributes.color}'
        )

    @staticmethod
    def _generate_note(term: Term) -> str:
        res = ''
        if term.attributes.note:
            note_text = term.attributes.note.replace('\\n', '\n')
            res = f'note right of {term.name}\n{note_text}\n    end note'
        return res

    @staticmethod
    def _generate_base_hierarchy(relationship: Relationship) -> str:
        relationships = {
            RelationshipType.DEPENDS.value: {
                RelationshipDirection.FORWARD: '...>',
                RelationshipDirection.BACKWARD: '<...',
                RelationshipDirection.BIDIRECTIONAL: '<...>',
            },
            RelationshipType.ASSOCIATION.value: {
                RelationshipDirection.FORWARD: '---',
                RelationshipDirection.BACKWARD: '---',
                RelationshipDirection.BIDIRECTIONAL: '---',
            },
            RelationshipType.DIRECT_ASSOCIATION.value: {
                RelationshipDirection.FORWARD: '--->',
                RelationshipDirection.BACKWARD: '<---',
                RelationshipDirection.BIDIRECTIONAL: '<--->',
            },
            RelationshipType.INHERITANCE.value: {
                RelationshipDirection.FORWARD: '---|>',
                RelationshipDirection.BACKWARD: '<|---',
                RelationshipDirection.BIDIRECTIONAL: '<|---|>',
            },
            RelationshipType.REALIZATION.value: {
                RelationshipDirection.FORWARD: '...|>',
                RelationshipDirection.BACKWARD: '<|...',
                RelationshipDirection.BIDIRECTIONAL: '<|...|>',
            },
            RelationshipType.AGGREGATION.value: {
                RelationshipDirection.FORWARD: '---o',
                RelationshipDirection.BACKWARD: 'o---',
                RelationshipDirection.BIDIRECTIONAL: 'o---o',
            },
            RelationshipType.COMPOSITION.value: {
                RelationshipDirection.FORWARD: '---*',
                RelationshipDirection.BACKWARD: '*---',
                RelationshipDirection.BIDIRECTIONAL: '*---*',
            },
        }
        leftchar: str = (
            ('"' + relationship.attributes.left_char + '"')
            if relationship.attributes.left_char
            else ''
        )
        rightchar: str = (
            ('"' + relationship.attributes.right_char + '"')
            if relationship.attributes.right_char
            else ''
        )
        title: str = (
            (': "' + relationship.attributes.title + '"')
            if relationship.attributes.title
            else ''
        )
        color: str = '[' + relationship.attributes.color + ']'
         
        relation: str = (
            relationships[relationship.relationship.value][
                relationship.attributes.direction
            ][:2]
            + color
            + relationships[relationship.relationship.value][
                relationship.attributes.direction
            ][2:]
        )
        res: str = ''
        res += (
            f'{relationship.parent.name} {leftchar} '
            f'{relation} '
            f'{rightchar} '
            f'{relationship.children[0].name} {title}'
        ) + '\n'
        return res

    @staticmethod
    def __prepare_function_term(function: Function):
        input_str: list[str] = [
            f'{el.term.name}: {el.label}' if el.label else str(el.term.name)
            for el in function.input_types
        ]
        output_str: str = (
            f'{function.output_type.term.name}: {function.output_type.label}'
            if function.output_type.label
            else str(function.output_type.term.name)
        )
        description: str = f'{", ".join(input_str)} -> {output_str}'
        return Term(
            function.name,
            function.label,
            description,
            TermAttributes(color=function.attributes.color),
        )

    @staticmethod
    def __prepare_function_hierarchy(function: Function, ontology: Ontology):
        relations = []
        input_types: collections.defaultdict[str, int] = collections.defaultdict(int)
        for input_type in function.input_types:
            input_types[input_type.term.name] += 1
        for k, v in input_types.items():
            term: Term = ontology.find_term_by_name(k)
            relations.append(
                Relationship(
                    term,
                    RelationshipType.from_str(function.attributes.type.value),
                    [Term(function.name)],
                    RelationshipAttrubutes(
                        color=function.attributes.color_arrow,
                        title=function.attributes.input_title,
                        left_char=f'{v if v != 1 else ""}',
                        direction=RelationshipDirection.FORWARD,
                    ),
                )
            )
        relations.append(
            Relationship(
                Term(function.name),
                RelationshipType.from_str(function.attributes.type.value),
                [ontology.find_term_by_name(function.output_type.term.name)],
                RelationshipAttrubutes(
                    color=function.attributes.color_arrow,
                    title=function.attributes.output_title,
                    direction=RelationshipDirection.FORWARD,
                ),
            )
        )
        return relations

    def _generate_type(self, term: Term) -> str:
        return f'class {term.name} {{\n  {term.description}\n}}'

    # TODO: add comments to input and output types and add color for block
    def _generate_function(self, function: Function) -> str:
        inputs: str = ', '.join(map(lambda t: t.term.name, function.input_types))
        outputs: str = function.output_type.term.name
        return (
            f'class {function.name} <<Function>> {{\n'
            f'  +{function.name}({inputs}) : ({outputs})\n'
            f'  {function.label}\n}}'
        )

    # TODO: check type of relationship
    def _generate_relationship(self, relationship: Relationship) -> str:
        return (
            f'note "{relationship.parent.name} {relationship.relationship.value} {list(map(lambda t: t.name, relationship.children))}" '
            f'as N{hash(relationship.parent.name) % 10000}'
        )

    def processes_puml_to_png(self, puml_file):
        outfile = os.path.splitext(puml_file)[0] + '.png'

        with open(puml_file, 'r', encoding='utf-8') as file:
            plantuml_text = file.read()

        data = zlib.compress(plantuml_text.encode('utf-8'))[2:-4]
        encoded_text = ''
        for i in range(0, len(data), 3):
            if i + 2 == len(data):
                encoded_text += self.__encode3bytes(data[i], data[i + 1], 0)
            elif i + 1 == len(data):
                encoded_text += self.__encode3bytes(data[i], 0, 0)
            else:
                encoded_text += self.__encode3bytes(data[i], data[i + 1], data[i + 2])

        url = f'{self.url}{encoded_text}'
        response = requests.get(url)

        if response.status_code == 200:
            with open(outfile, 'wb') as out:
                out.write(response.content)

    @staticmethod
    def __encode3bytes(b1, b2, b3):
        chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_'
        c1 = b1 >> 2
        c2 = ((b1 & 0x3) << 4) | (b2 >> 4)
        c3 = ((b2 & 0xF) << 2) | (b3 >> 6)
        c4 = b3 & 0x3F
        return chars[c1] + chars[c2] + chars[c3] + chars[c4]
