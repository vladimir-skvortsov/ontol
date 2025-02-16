from parser.oast import Ontology, Term, Function, Relationship, Meta
from datetime import datetime
import re


class Parser:

    @staticmethod
    def parse(file_content: str) -> Ontology:
        ontology: Ontology = Ontology()

        lines: list[str] = file_content.splitlines()

        for line in lines:
            line: str = line.strip()

            if line.startswith('#'):
                continue
            elif line.startswith('type'):
                type_def: Term = Parser._parse_type(line)
                ontology.add_type(type_def)
            elif line.startswith('function'):
                func_def: Function = Parser._parse_function(line)
                ontology.add_function(func_def)
            elif line.startswith('meta'):
                meta: Meta = Parser._parse_meta(line)
                ontology.set_meta(meta)
            elif line:
                relationship: Relationship = Relationship(line)
                ontology.add_relationship(relationship)

        return ontology

    @staticmethod
    def _parse_type(line: str) -> Term:
        parts: list[str] = line.split()
        name: str = parts[1]
        description: str | None = ' '.join(parts[2:])[1:-1] if len(parts) > 2 else None
        return Term(name, description)

    @staticmethod
    def _parse_function(line: str) -> Function:
        parts: list[str] = line.split()
        name: str = parts[1]
        input_types: list[str] = parts[2].strip('()').split(',')
        output_types: list[str] = parts[3].strip('()').split(',')
        label: str | None = parts[4] if len(parts) > 4 else None
        description: str | None = ' '.join(parts[5:]) if len(parts) > 5 else None
        return Function(name, input_types, output_types, label, description)

    @staticmethod
    def _parse_meta(line: str) -> Meta:
        parts: list[str] = re.findall(r'\"[^\"]*\"|\S+', line)

        version: str = parts[1]
        name: str = parts[2].strip('"')
        author: str = parts[3].strip('"')
        description: str | None = (
            ' '.join(parts[4:]).strip('"') if len(parts) > 4 else ''
        )
        date_created: str = datetime.today().strftime('%Y-%m-%d')
        return Meta(version, name, author, description, date_created)
