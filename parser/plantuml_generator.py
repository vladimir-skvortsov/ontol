from oast import Function, Ontology, Relationship, Term


# TODO: make look like in technical task
class PlantUMLGenerator:
    def generate(self, ontology: Ontology) -> str:
        uml_lines: list[str] = ['@startuml', 'skinparam classAttributeIconSize 0']

        if ontology.meta:
            uml_lines.append(f'title {ontology.meta.name} by {ontology.meta.author}')

        for type_def in ontology.types:
            uml_lines.append(self._generate_type(type_def))

        for func_def in ontology.functions:
            uml_lines.append(self._generate_function(func_def))

        for expr in ontology.hierarchy:
            uml_lines.append(self._generate_logical_expression(expr))

        uml_lines.append('@enduml')
        return '\n'.join(uml_lines)

    def _generate_type(self, type_def: Term) -> str:
        return f'class {type_def.name} {{\n  {type_def.description}\n}}'

    def _generate_function(self, func_def: Function) -> str:
        inputs: str = ', '.join(func_def.input_types)
        outputs: str = ', '.join(func_def.output_types)
        return (
            f'class {func_def.name} <<Function>> {{\n'
            f'  +{func_def.name}({inputs}) : ({outputs})\n'
            f'  {func_def.description}\n}}'
        )

    def _generate_logical_expression(self, logical_expr: Relationship) -> str:
        return f'note "{logical_expr.expression}" as N{hash(logical_expr.expression) % 10000}'
