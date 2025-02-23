import os
import zlib

import requests

from ontol import Function, Ontology, Relationship, Term


# TODO: make look like in technical task
class PlantUML:
    SERVER_URL = 'http://www.plantuml.com/plantuml/img/'

    def __init__(self, url=SERVER_URL):
        self.url = url

    def generate(self, ontology: Ontology) -> str:
        if ontology.meta.type == 'Базовый':
            return self._generate_novikov(ontology)
        else:
            return self._generate_base(ontology)

    def _generate_base(self, ontology: Ontology) -> str:
        uml_lines: list[str] = ['@startuml', 'skinparam classAttributeIconSize 0']

        if ontology.meta:
            uml_lines.append(f'title {ontology.meta.name} by {ontology.meta.author}')

        for term in ontology.types:
            uml_lines.append(self._generate_type(term))

        for function in ontology.functions:
            uml_lines.append(self._generate_function(function))

        for relationship in ontology.hierarchy:
            uml_lines.append(self._generate_relationship(relationship))

        uml_lines.append('@enduml')
        return '\n'.join(uml_lines)

    def _generate_novikov(self, ontology: Ontology) -> str:
        uml_lines: list[str] = [
            '@startuml',
            'skinparam backgroundColor #F0F8FF',
            'skinparam defaultTextAlignment center',
            'skinparam shadowing false',
        ]

        if not ontology.meta:
            raise ValueError('No meta defined for ontology')
        if ontology.functions:
            raise ValueError('Functions is not available for these diagram types')

        uml_lines.append(f'package "{ontology.meta.name}" {{')

        for term in ontology.types:
            uml_lines.append(self._generate_rectangle(term))

        for relationship in ontology.hierarchy:
            uml_lines.append(self._generate_base_hierarchy(relationship))

        uml_lines.append('}')
        uml_lines.append('@enduml')
        return '\n'.join(uml_lines)

    def _generate_rectangle(self, term: Term) -> str:
        return (
    f'rectangle "{term.label}' +
    (f'\\n({term.description})' if term.description else '') +
    f'" as {term.name} {term.attributes["color"]}'
)

    def _generate_base_hierarchy(self, relationship: Relationship) -> str:
        relationships = {'depends': '..>'}
        return (
            f'{relationship.parent} '
            f'{relationships[relationship.relationship]} '
            f'{relationship.child}'
        )

    def _generate_type(self, term: Term) -> str:
        return f'class {term.name} {{\n  {term.description}\n}}'

    def _generate_function(self, function: Function) -> str:
        inputs: str = ', '.join(map(lambda t: t[0], function.input_types))
        outputs: str = function.output_type[0]
        return (
            f'class {function.name} <<Function>> {{\n'
            f'  +{function.name}({inputs}) : ({outputs})\n'
            f'  {function.label}\n}}'
        )

    def _generate_relationship(self, relationship: Relationship) -> str:
        return f'note "{relationship.parent} {relationship.relationship} {relationship.child}" as N{hash(relationship.parent) % 10000}'

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
