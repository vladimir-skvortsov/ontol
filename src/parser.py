import re
from src import Ontology, Term, Function, Relationship, Meta
from datetime import datetime


class Parser:
    @staticmethod
    def parse(file_content: str) -> Ontology:
        ontology = Ontology()

        lines = file_content.splitlines()
        current_block = None
        meta_data = {
            'version': None,
            'name': None,
            'author': None,
            'description': None,
            'date_created': datetime.today().strftime('%Y-%m-%d'),
        }

        for line in lines:
            line = line.strip()

            if line.startswith('#') or not line:
                continue

            # TODO: send a warning if the user specified some meta information twice
            if re.match(r'^version\s+', line):
                meta_data['version'] = Parser._parse_meta_line(line, 'version')
            elif re.match(r'^title\s+', line):
                meta_data['name'] = Parser._parse_meta_line(line, 'title')
            elif re.match(r'^author\s+', line):
                meta_data['author'] = Parser._parse_meta_line(line, 'author')
            elif re.match(r'^desc\s+', line):
                meta_data['description'] = Parser._parse_meta_line(line, 'desc')

            elif line.startswith('types:'):
                current_block = 'types'
                continue
            elif line.startswith('functions:'):
                current_block = 'functions'
                continue
            elif line.startswith('hierarchy:'):
                current_block = 'hierarchy'
                continue

            elif current_block == 'types':
                type_def = Parser._parse_type(line)
                ontology.add_type(type_def)
            elif current_block == 'functions':
                func_def = Parser._parse_function(line)
                ontology.add_function(func_def)
            elif current_block == 'hierarchy':
                relationship = Parser._parse_relationship(line)
                ontology.add_relationship(relationship)

        ontology.set_meta(Meta(**meta_data))

        return ontology

    @staticmethod
    def _parse_meta_line(line: str, key: str) -> str:
        match = re.match(rf"{key}\s+['\"](.+?)['\"]", line)
        if match:
            return match.group(1)
        raise ValueError(f'Invalid {key} format')

    @staticmethod
    def _parse_type(line: str) -> Term:
        match = re.match(
            r"(\w+):\s*['\"](.+?)['\"],\s*['\"](.+?)['\"](,\s*\{(.+?)\})?$", line
        )
        if match:
            name = match.group(1)
            label = match.group(2)
            description = match.group(3)
            attributes = (
                Parser._parse_attributes(match.group(5)) if match.group(5) else {}
            )
            return Term(name, label, description, attributes)
        print(match, line)
        raise ValueError('Invalid type format')

    @staticmethod
    def _parse_attributes(attr_string: str) -> dict:
        attributes = {}
        if attr_string:
            # Убираем фигурные скобки и разбиваем по запятым
            attr_string = attr_string.strip('{}').strip()
            for attr in attr_string.split(','):
                key, value = attr.split(':', 1)
                attributes[key.strip()] = value.strip().strip('\'"')
        return attributes

    @staticmethod
    def _parse_function(line: str) -> Function:
        line = line.split('#', 1)[0].strip()

        match = re.match(
            r"(\w+):\s*['\"](.*?)['\"]\s*\((.*?)\)\s*->\s*(\w+):\s*['\"](.*?)['\"]$",
            line,
        )
        if match:
            name = match.group(1)
            label = match.group(2)
            input_params = Parser._parse_parameters(match.group(3))
            output_type = match.group(4)
            output_label = match.group(5)
            return Function(name, label, input_params, (output_type, output_label))
        raise ValueError('Invalid function format')

    @staticmethod
    def _parse_parameters(param_string: str) -> list:
        params = []
        for param in param_string.split(','):
            param = param.strip()
            match = re.match(r"(\w+):\s*['\"](.*?)['\"]$", param)
            if match:
                param_name = match.group(1)
                param_description = match.group(2) if match.group(2) else None
                params.append((param_name, param_description))
        return params

    @staticmethod
    def _parse_relationship(line: str) -> Relationship:
        parts = line.split()
        if len(parts) == 3:
            return Relationship(parts[0], parts[1], parts[2])
        raise ValueError('Invalid hierarchy format')
