import re
from src import Ontology, Term, Function, Relationship, Meta
from datetime import datetime


class Parser:
    def __init__(self):
        self.warnings = []

    def parse(self, file_content: str, file_path: str) -> tuple[Ontology, list]:
        self.warnings.clear()

        ontology = Ontology()

        lines = file_content.splitlines()
        current_block = None
        meta_data = {
            'version': None,
            'name': None,
            'author': None,
            'description': None,
            'type': None,
            'date_created': datetime.today().strftime('%Y-%m-%d'),
        }

        for index, line in enumerate(lines):
            line_number = index + 1
            line = line.strip()

            if line.startswith('#') or not line:
                continue

            try:
                if re.match(r'^version\s+', line):
                    meta_data['version'] = self._parse_meta_line(line, 'version')
                elif re.match(r'^title\s+', line):
                    meta_data['name'] = self._parse_meta_line(line, 'title')
                elif re.match(r'^author\s+', line):
                    meta_data['author'] = self._parse_meta_line(line, 'author')
                elif re.match(r'^desc\s+', line):
                    meta_data['description'] = self._parse_meta_line(line, 'desc')
                elif re.match(r'^type\s+', line):
                    meta_data['type'] = self._parse_meta_line(line, 'type')

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
                raise Exception(
                    f'File "{file_path}", line {line_number}\n    {line}\n{type(e).__name__}: {e}'
                )

        ontology.set_meta(Meta(**meta_data))

        # Возвращаем объект онтологии и список предупреждений
        return ontology, self.warnings

    def _parse_meta_line(self, line: str, key: str) -> str:
        match = re.match(rf"{key}\s+['\"](.*?)['\"]", line)

        if not match:
            raise SyntaxError(f'Invalid {key} format')

        return match.group(1)

    def _parse_type(self, line: str, file_path: str, line_number: int) -> Term:
        match = re.match(
            r"(\w+):\s*['\"](.*?)['\"],\s*['\"](.*?)['\"](,\s*\{(.*?)\})?$", line
        )

        if not match:
            raise SyntaxError('Invalid type format')

        name = match.group(1)
        label = match.group(2)
        description = match.group(3)

        if not label:
            self._add_warning(file_path, line_number, line, 'Label is empty for type.')
        if not description:
            self._add_warning(
                file_path, line_number, line, 'Description is empty for type.'
            )

        attributes = self._parse_attributes(match.group(5)) if match.group(5) else {}

        return Term(name, label, description, attributes)

    def _parse_attributes(self, attr_string: str) -> dict:
        attributes = {}
        if attr_string:
            attr_string = attr_string.strip('{}').strip()
            for attr in attr_string.split(','):
                key, value = attr.split(':', 1)
                attributes[key.strip()] = value.strip().strip('\'"')
        return attributes

    def _parse_function(self, line: str, file_path: str, line_number: int) -> Function:
        line = line.split('#', 1)[0].strip()

        match = re.match(
            r"(\w+):\s*['\"](.*?)['\"]\s*\((.*?)\)\s*->\s*(\w+):\s*['\"](.*?)['\"]$",
            line,
        )

        if not match:
            raise SyntaxError('Invalid function format')

        name = match.group(1)
        label = match.group(2)
        input_params = self._parse_parameters(match.group(3))
        output_type = match.group(4)
        output_label = match.group(5)

        if not label:
            self._add_warning(file_path, line_number, line, 'Label is empty')
        if not output_label:
            self._add_warning(file_path, line_number, line, 'Output label is empty')

        return Function(name, label, input_params, (output_type, output_label))

    def _parse_parameters(self, param_string: str) -> list:
        params = []

        for param in param_string.split(','):
            param = param.strip()
            match = re.match(r"(\w+):\s*['\"](.*?)['\"]$", param)

            if match:
                param_name = match.group(1)
                param_description = match.group(2) if match.group(2) else None
                params.append((param_name, param_description))

        return params

    def _parse_relationship(self, line: str) -> Relationship:
        parts = line.split()

        if len(parts) != 3:
            raise SyntaxError('Invalid hierarchy format')

        return Relationship(parts[0], parts[1], parts[2])

    def _add_warning(
        self, file_path: str, line_number: int, line: str, message: str
    ) -> None:
        warning = (
            f'File "{file_path}", line {line_number}\n    {line}\nWarning: {message}'
        )
        self.warnings.append(warning)
