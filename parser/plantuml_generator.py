from parser import Function, Ontology, Relationship, Term


# TODO: make look like in technical task
class PlantUMLGenerator:
    def generate(self, ontology: Ontology) -> str:
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

    def _generate_type(self, term: Term) -> str:
        return f'class {term.name} {{\n  {term.description}\n}}'

    def _generate_function(self, function: Function) -> str:
        inputs: str = ', '.join(map(lambda t: t[0], function.input_types))
        outputs: str = ', '.join(map(lambda t: t[0], function.output_types))
        return (
            f'class {function.name} <<Function>> {{\n'
            f'  +{function.name}({inputs}) : ({outputs})\n'
            f'  {function.description}\n}}'
        )

    def _generate_relationship(self, relationship: Relationship) -> str:
        return f'note "{relationship.parent} {relationship.relationship} {relationship.child}" as N{hash(relationship.parent) % 10000}'
