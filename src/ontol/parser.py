from sly import Lexer as BaseLexer, Parser as BaseParser
from datetime import datetime
from typing import Literal, Optional

from ontol import (
    Ontology,
    Term,
    Function,
    Relationship,
    FunctionArgument,
    RelationshipType,
)


class Lexer(BaseLexer):
    tokens = {
        META_VERSION,
        META_TITLE,
        META_AUTHOR,
        META_DESC,
        META_DATE,
        META_TYPE,
        TYPES_BLOCK,
        FUNCTIONS_BLOCK,
        HIERARCHY_BLOCK,
        STRING,
        IDENTIFIER,
        LBRACE,
        RBRACE,
        COLON,
        COMMA,
        ARROW,
        LPAREN,
        RPAREN,
        NEWLINE,
    }

    # String containing ignored characters (spaces and tabs)
    ignore: str = ' \t'

    # Regular expression rules for tokens
    TYPES_BLOCK: str = r'types:'
    FUNCTIONS_BLOCK: str = r'functions:'
    HIERARCHY_BLOCK: str = r'hierarchy:'

    META_VERSION: str = r'version:'
    META_TITLE: str = r'title:'
    META_AUTHOR: str = r'author:'
    META_DESC: str = r'desc:'
    META_DATE: str = r'date:'
    META_TYPE: str = r'type:'

    STRING: str = r'\'[^\']*\'|\"[^\"]*\"'
    IDENTIFIER: str = r'[a-zA-Z_][a-zA-Z0-9_]*'

    LBRACE: str = r'\{'
    RBRACE: str = r'\}'
    COLON: str = r':'
    COMMA: str = r','
    ARROW: str = r'->'

    LPAREN: str = r'\('
    RPAREN: str = r'\)'

    ignore_comment: str = r'\#.*'

    # Newline handling
    @_(r'\n+')
    def NEWLINE(self, t):
        self.lineno += t.value.count('\n')
        return t

    # Strings handling
    def STRING(self, t):
        t.value = t.value[1:-1]  # Remove quotes
        return t

    def error(self, t) -> None:
        self.index += 1
        raise SyntaxError(f"Illegal character '{t.value[0]}'")


class Parser(BaseParser):
    tokens = Lexer.tokens
    expected_shift_reduce: int = 22

    def __init__(self) -> None:
        self.ontology: Ontology = Ontology()
        self.__warnings: list[str] = []

    def parse(self, file_content: str, file_path: str) -> tuple[Ontology, list[str]]:
        self.__warnings.clear()

        self.__lines = file_content.splitlines()
        self.__file_path = file_path

        lexer: Lexer = Lexer()
        tokens: list = lexer.tokenize(file_content)
        # print(', '.join([token.type for token in tokens]))
        ontology: Ontology = super().parse(tokens)

        return ontology, self.__warnings

    def _get_exception_message(
        self, token, message: str, type: Literal['warning', 'error'] = 'warning'
    ) -> str:
        line_number = token.lineno
        line: str = self.__lines[line_number - 1]
        line_padding: int = 4
        message_prefix: str = (
            '\033[33mWarning' if type == 'warning' else '\033[31mError'
        )

        final_message: str = f'File "{self.__file_path}", line {line_number}'
        final_message += f'\n{" " * line_padding}{line}'
        if token is not None:
            line_start_index = sum(
                len(line) + 1 for line in self.__lines[: line_number - 1]
            )
            column_index = token.index - line_start_index - 1
            final_message += f'\n {" " * line_padding}{" " * column_index}^'
        final_message += (
            f'\n{message_prefix}: \033[0m{message[0].lower() + message[1:]}'
        )

        return final_message

    def _add_warning(self, token, message: str) -> None:
        final_message: str = self._get_exception_message(token, message, 'warning')
        self.__warnings.append(final_message)

    @_('statement_list')
    def program(self, p) -> Ontology:
        if not self.ontology.meta.date_created:
            self.ontology.meta.date_created = datetime.today().strftime('%Y-%m-%d')
        return self.ontology

    @_('statement_list statement', '')
    def statement_list(self, p) -> None:
        pass

    @_('statement')
    def statement_list(self, p) -> None:
        pass

    @_('META_VERSION STRING NEWLINE')
    def statement(self, p) -> None:
        if not p.STRING:
            self._add_warning(p._slice[1], 'Version value is empty')

        self.ontology.meta.version = p.STRING

    @_('META_TITLE STRING NEWLINE')
    def statement(self, p) -> None:
        if not p.STRING:
            self._add_warning(p._slice[1], 'Title value is empty')

        self.ontology.meta.title = p.STRING

    @_('META_AUTHOR STRING NEWLINE')
    def statement(self, p) -> None:
        if not p.STRING:
            self._add_warning(p._slice[1], 'Author value is empty')

        self.ontology.meta.author = p.STRING

    @_('META_DESC STRING NEWLINE')
    def statement(self, p) -> None:
        if not p.STRING:
            self._add_warning(p._slice[1], 'Description value is empty')

        self.ontology.meta.description = p.STRING

    @_('META_DATE STRING NEWLINE')
    def statement(self, p) -> None:
        if not p.STRING:
            self._add_warning(p._slice[1], 'Date value is empty')

        self.ontology.meta.date_created = p.STRING

    @_('META_TYPE STRING NEWLINE')
    def statement(self, p) -> None:
        if not p.STRING:
            self._add_warning(p._slice[1], 'Type value is empty')

        self.ontology.meta.type = p.STRING

    @_('TYPES_BLOCK NEWLINE type_list')
    def statement(self, p) -> None:
        pass

    @_(
        'type_list type NEWLINE',
        'type NEWLINE',
        'NEWLINE type_list',
        '',
    )
    def type_list(self, p) -> None:
        pass

    @_('IDENTIFIER COLON STRING COMMA STRING attributes')
    def type(self, p) -> None:
        existing_term: Optional[Term] = self.ontology.find_term_by_name(p.IDENTIFIER)

        if existing_term is not None:
            raise ValueError(
                self._get_exception_message(
                    p._slice[0],
                    f"Type '{p.IDENTIFIER}' has already been declared",
                    'error',
                )
            )

        term = Term(
            name=p.IDENTIFIER,
            label=p.STRING0,
            description=p.STRING1,
            attributes=p.attributes,
        )

        if not p.STRING0:
            self._add_warning(p._slice[2], 'Term label is empty')

        if not p.STRING1:
            self._add_warning(p._slice[4], 'Term description is empty')

        self.ontology.add_type(term)

    @_('FUNCTIONS_BLOCK NEWLINE function_list')
    def statement(self, p) -> None:
        pass

    @_(
        'function_list function NEWLINE',
        'function NEWLINE',
        'NEWLINE function_list',
        '',
    )
    def function_list(self, p) -> None:
        pass

    @_('IDENTIFIER COLON STRING params ARROW IDENTIFIER COLON STRING attributes')
    def function(self, p) -> None:
        existing_function: Optional[Function] = self.ontology.find_function_by_name(
            p.IDENTIFIER0
        )

        if existing_function is not None:
            raise ValueError(
                self._get_exception_message(
                    p._slice[0],
                    f"Function '{p.IDENTIFIER0}' has already been declared",
                    'error',
                )
            )

        input_types = p.params

        output_term: Optional[Term] = self.ontology.find_term_by_name(p.IDENTIFIER1)

        if output_term is None:
            raise ValueError(
                self._get_exception_message(p._slice[5], 'Undefined term', 'error')
            )

        output_type: FunctionArgument = FunctionArgument(output_term, p.STRING1)

        function: Function = Function(
            name=p.IDENTIFIER0,
            label=p.STRING0,
            input_types=input_types,
            output_type=output_type,
            attributes=p.attributes,
        )

        if not p.STRING0:
            self._add_warning(p._slice[2], 'Label is empty')

        if not p.STRING1:
            self._add_warning(p._slice[7], 'Output term label is empty')

        self.ontology.add_function(function)

    @_(
        'LPAREN param_list RPAREN',
        'LPAREN NEWLINE param_list RPAREN',
        'LPAREN param_list NEWLINE RPAREN',
        'LPAREN NEWLINE param_list NEWLINE RPAREN',
        'LPAREN NEWLINE param_list COMMA NEWLINE RPAREN',
    )
    def params(self, p) -> list[FunctionArgument]:
        params: list[FunctionArgument] = []

        for param in p.param_list:
            term_token = param[0]
            term_name: str = term_token.value
            label_token = param[1]
            param_label: str = label_token.value

            term: Optional[Term] = self.ontology.find_term_by_name(term_name)

            if term is None:
                raise ValueError(
                    self._get_exception_message(term_token, 'Undefined term', 'error')
                )

            if not param_label:
                self._add_warning(label_token, 'Parameter label is empty')

            params.append(FunctionArgument(term, param_label))

        return params

    @_('')
    def param_list(self, p) -> list[tuple]:
        return []

    @_('param')
    def param_list(self, p) -> list[tuple]:
        return [p.param]

    @_(
        'param_list COMMA param',
        'param_list COMMA NEWLINE param',
    )
    def param_list(self, p) -> list[tuple]:
        return p.param_list + [p.param]

    @_('IDENTIFIER COLON STRING')
    def param(self, p) -> tuple:
        return (p._slice[0], p._slice[2])

    @_('HIERARCHY_BLOCK NEWLINE hierarchy_list')
    def statement(self, p) -> None:
        pass

    @_('hierarchy_list hierarchy NEWLINE')
    def hierarchy_list(self, p) -> None:
        pass

    @_('hierarchy NEWLINE')
    def hierarchy_list(self, p) -> None:
        pass

    @_('IDENTIFIER IDENTIFIER IDENTIFIER attributes')
    def hierarchy(self, p) -> None:
        parent: Optional[Term] = self.ontology.find_term_by_name(p.IDENTIFIER0)

        if parent is None:
            raise ValueError(
                self._get_exception_message(p._slice[0], 'Undefined term', 'error')
            )

        relationship = RelationshipType.from_str(p.IDENTIFIER1)

        if relationship is None:
            raise ValueError(
                self._get_exception_message(
                    p._slice[1], 'Unexpected relationship type', 'error'
                )
            )

        child_term: Optional[Term] = self.ontology.find_term_by_name(p.IDENTIFIER2)

        if child_term is None:
            raise ValueError(
                self._get_exception_message(p._slice[2], 'Undefined term', 'error')
            )

        children: list[Term] = [child_term]

        relationship = Relationship(
            parent=parent,
            relationship=relationship,
            children=children,
            attributes=p.attributes,
        )
        self.ontology.add_relationship(relationship)

    @_(
        'COMMA LBRACE attribute_list RBRACE',
        'COMMA LBRACE NEWLINE attribute_list RBRACE',
        'COMMA LBRACE attribute_list NEWLINE RBRACE',
        'COMMA LBRACE NEWLINE attribute_list NEWLINE RBRACE',
        'COMMA LBRACE NEWLINE attribute_list COMMA NEWLINE RBRACE',
    )
    def attributes(self, p) -> dict[str, str]:
        return p.attribute_list

    @_('')
    def attributes(self, p) -> dict[str, str]:
        return {}

    @_(
        'attribute_list COMMA attribute',
        'attribute_list COMMA NEWLINE attribute',
    )
    def attribute_list(self, p) -> dict[str, str]:
        p.attribute_list.update(p.attribute)
        return p.attribute_list

    @_('attribute')
    def attribute_list(self, p) -> dict[str, str]:
        return p.attribute

    @_('')
    def attribute_list(self, p) -> dict[str, str]:
        return {}

    @_('IDENTIFIER COLON STRING')
    def attribute(self, p) -> dict[str, str]:
        if not p.STRING:
            self._add_warning(p._slice[2], 'Attribute value is empty')

        return {p.IDENTIFIER: p.STRING}

    @_('NEWLINE')
    def statement(self, p) -> None:
        pass

    def error(self, p) -> None:
        if p:
            raise SyntaxError(
                self._get_exception_message(
                    p,
                    f'Syntax error {p.type}',
                    'error',
                )
            )

        raise SyntaxError('Syntax error at EOF')
