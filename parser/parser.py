import re
from oast import Ontology, Term, Function, Relationship, Meta
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

        # Установка метаинформации после обработки всех строк
        ontology.set_meta(Meta(**meta_data))

        return ontology

    @staticmethod
    def _parse_meta_line(line: str, key: str) -> str:
        """Парсит строку метаинформации и возвращает значение."""
        match = re.match(rf"{key}\s+['\"](.+?)['\"]", line)
        if match:
            return match.group(1)
        raise ValueError(f'Invalid {key} format')

    @staticmethod
    def _parse_type(line: str) -> Term:
        """Парсит строку определения типа."""
        match = re.match(r"(\w+):?\s*['\"]?(.*?)['\"]?$", line)
        if match:
            name = match.group(1)
            description = match.group(2) if match.group(2) else None
            return Term(name, description)
        raise ValueError('Invalid type format')

    @staticmethod
    def _parse_function(line: str) -> Function:
        line = line.split('#', 1)[0].strip()

        # Регулярное выражение для разбора строки функции
        match = re.match(
            r"(\w+):?\s*['\"]?(.*?)['\"]?\s*\((.*?)\)\s*->\s*(\w+):?\s*['\"]?(.*?)['\"]?$",
            line,
        )
        if match:
            name = match.group(1)
            description = match.group(2) if match.group(2) else None
            input_params = Parser._parse_parameters(match.group(3))
            output_type = match.group(4)
            output_description = match.group(5) if match.group(5) else None
            return Function(
                name, input_params, output_type, description, output_description
            )
        raise ValueError('Invalid function format')

    @staticmethod
    def _parse_parameters(param_string: str) -> list:
        """Парсит параметры функции."""
        params = []
        for param in param_string.split(','):
            param = param.strip()
            match = re.match(r"(\w+):?\s*['\"]?(.*?)['\"]?$", param)
            if match:
                param_name = match.group(1)
                param_description = match.group(2) if match.group(2) else None
                params.append((param_name, param_description))
        return params

    @staticmethod
    def _parse_relationship(line: str) -> Relationship:
        """Парсит строку иерархического выражения."""
        parts = line.split()
        if len(parts) == 3:
            return Relationship(parts[0], parts[1], parts[2])
        raise ValueError('Invalid hierarchy format')
