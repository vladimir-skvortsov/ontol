import re

from typing import Optional, Literal
from ontol import Ontology, Term, Function, Relationship, Meta
from datetime import datetime


class Parser:
    def __init__(self):
        self.warnings: list[str] = []

    def parse(self, file_content: str, file_path: str) -> tuple[Ontology, list]:
        self.warnings.clear()

        ontology: Ontology = Ontology()

        lines: list[str] = file_content.splitlines()
        current_block: Optional[Literal['types', 'functions', 'hierarchy']] = None
        meta_data: dict[str, Optional[str]] = {
            'version': None,
            'name': None,
            'author': None,
            'description': None,
            'type': None,
            'date_created': datetime.today().strftime('%Y-%m-%d'),
        }

        for index, line in enumerate(lines):
            line_number: int = index + 1
            line = line.strip()

            if line.startswith('#') or not line:
                continue

            try:
                if re.match(r'^version:\s+', line):
                    meta_data['version'] = self._parse_meta_line(
                        line, 'version', file_path, line_number
                    )
                elif re.match(r'^title:\s+', line):
                    meta_data['name'] = self._parse_meta_line(
                        line, 'title', file_path, line_number
                    )
                elif re.match(r'^author:\s+', line):
                    meta_data['author'] = self._parse_meta_line(
                        line, 'author', file_path, line_number
                    )
                elif re.match(r'^desc:\s+', line):
                    meta_data['description'] = self._parse_meta_line(
                        line, 'desc', file_path, line_number
                    )
                elif re.match(r'^type:\s+', line):
                    meta_data['type'] = self._parse_meta_line(
                        line, 'type', file_path, line_number
                    )

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
                    type_def = self._parse_type(line, file_path, line_number)
                    ontology.add_type(type_def)
                elif current_block == 'functions':
                    func_def = self._parse_function(line, file_path, line_number)
                    ontology.add_function(func_def)
                elif current_block == 'hierarchy':
                    relationship = self._parse_relationship(line)
                    ontology.add_relationship(relationship)

                else:
                    raise SyntaxError('Unexpected line')

            except Exception as e:
                raise SyntaxError(
                    f'File "{file_path}", line {line_number}\n    {line}\n\033[31m{type(e).__name__}: \033[0m{e}'
                )

        ontology.set_meta(Meta(**meta_data))

        return ontology, self.warnings

    def _parse_meta_line(
        self, line: str, key: str, file_path: str, line_number: int
    ) -> str:
        match = re.match(rf"{key}:\s+['\"](.*?)['\"]", line)

        if not match:
            raise SyntaxError(f'Invalid {key} format')

        value = match.group(1)

        if not value:
            self._add_warning(file_path, line_number, line, 'Meta value is empty')

        return value

    def _parse_type(self, line: str, file_path: str, line_number: int) -> Term:
        match = re.match(
            r"(\w+):\s*['\"](.*?)['\"],\s*['\"](.*?)['\"](,\s*\{(.*?)\})?$", line
        )

        if not match:
            raise SyntaxError('Invalid type format')

        name: str = match.group(1)
        label: str = match.group(2)
        description: str = match.group(3)

        if not label:
            self._add_warning(file_path, line_number, line, 'Label is empty')
        if not description:
            self._add_warning(file_path, line_number, line, 'Description is empty')

        attributes: dict[str, str] = (
            self._parse_attributes(match.group(5)) if match.group(5) else {}
        )

        return Term(name, label, description, attributes)

    def _parse_attributes(self, attr_string: str) -> dict[str, str]:
        attributes: dict[str, str] = {}

        if attr_string:
            attr_string = attr_string.strip('{}').strip()
            for attr in attr_string.split(','):
                key, value = attr.split(':', 1)
                attributes[key.strip()] = value.strip().strip('\'"')

        return attributes

    def _parse_function(self, line: str, file_path: str, line_number: int) -> Function:
        match = re.match(
            r"(\w+):\s*['\"](.*?)['\"]\s*\((.*?)\)\s*->\s*(\w+):\s*['\"](.*?)['\"](,\s*\{(.*?)\})?$",
            line,
        )

        if not match:
            raise SyntaxError('Invalid function format')

        name: str = match.group(1)
        label: str = match.group(2)
        input_params: list[tuple[str, str]] = self._parse_parameters(
            match.group(3), line, file_path, line_number
        )
        output_type: str = match.group(4)
        output_label: str = match.group(5)
        attributes: dict[str, str] = (
            self._parse_attributes(match.group(7)) if match.group(7) else {}
        )

        if not label:
            self._add_warning(file_path, line_number, line, 'Label is empty')
        if not output_label:
            self._add_warning(file_path, line_number, line, 'Output label is empty')

        return Function(
            name, label, input_params, (output_type, output_label), attributes
        )

    def _parse_parameters(
        self, params_string: str, line: str, file_path: str, line_number: int
    ) -> list[tuple[str, str]]:
        params: list[tuple[str, str]] = []

        for param in params_string.split(','):
            param = param.strip()
            match = re.match(r"(\w+):\s*['\"](.*?)['\"]$", param)

            if match:
                param_name: str = match.group(1)
                param_label: str = match.group(2)

                if not param_label:
                    self._add_warning(
                        file_path,
                        line_number,
                        line,
                        f"{param_name}'s parameter label is empty",
                    )

                params.append((param_name, param_label))

        return params

    def _parse_relationship(self, line: str) -> Relationship:
        pattern = r'^(\w+)\s+(\w+)\s+(?:\(([^)]+)\)|(\w+))?\s*(?:\{([^}]*)\})?$'
        match = re.match(pattern, line.strip())
        if not match:
            raise ValueError(f'Invalid line {line}')

        parent: str = match.group(1)
        relation: str = match.group(2)
        child: str = match.group(3) or match.group(4)
        children: list[str] = child.split(', ') if child else []

        attributes = match.group(5)
        attributes_dict = {
            'color': '#black',
            'title': '',
            'leftChar': '',
            'rightChar': '',
            'direction': 'forward',
        }

        if attributes:
            for item in attributes.split(', '):
                key, value = item.split(': ', 1)
                attributes_dict[key.strip()] = value.strip().strip('"\'')

        return Relationship(parent, relation, children, attributes_dict)

    def _add_warning(
        self, file_path: str, line_number: int, line: str, message: str
    ) -> None:
        warning: str = f'File "{file_path}", line {line_number}\n    {line}\n\033[33mWarning: \033[0m{message}'
        self.warnings.append(warning)
