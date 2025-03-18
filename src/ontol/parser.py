from sly import Lexer as BaseLexer, Parser as BaseParser
from datetime import datetime
from typing import Literal, Optional, Any, Type
from dataclasses import fields

from ontol import (
    constants,
    Ontology,
    Figure,
    Term,
    Function,
    Relationship,
    Meta,
    FunctionArgument,
    RelationshipType,
    RelationshipAttributes,
    TermAttributes,
    FunctionAttributes,
    RelationshipDirection,
)


class Lexer(BaseLexer):
    tokens = {
        TYPES_BLOCK,
        FUNCTIONS_BLOCK,
        HIERARCHY_BLOCK,
        FIGURE_BLOCK,
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
    TYPES_BLOCK: str = r'types'
    FUNCTIONS_BLOCK: str = r'functions'
    HIERARCHY_BLOCK: str = r'hierarchy'
    FIGURE_BLOCK: str = r'figure'

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
        raise SyntaxError(f"{constants.error_prefix} illegal character '{t.value[0]}'")


class Parser(BaseParser):
    tokens = Lexer.tokens
    expected_shift_reduce: int = 24

    def __init__(self) -> None:
        self.__ontology: Ontology = Ontology()
        self.__warnings: list[str] = []

    def parse(self, file_content: str, file_path: str) -> tuple[Ontology, list[str]]:
        self.__warnings.clear()

        self.__lines: list[str] = file_content.splitlines()
        self.__file_path: str = file_path
        self.__ontology: Ontology = Ontology()

        lexer: Lexer = Lexer()
        tokens: list = lexer.tokenize(file_content)

        super().parse(tokens)

        return self.__ontology, self.__warnings

    def _get_exception_message(
        self, token, message: str, type: Literal['warning', 'error'] = 'warning'
    ) -> str:
        line_number = token.lineno
        line: str = self.__lines[line_number - 1]
        line_padding: int = 4
        message_prefix: str = (
            constants.warning_prefix if type == 'warning' else constants.error_prefix
        )

        final_message: str = f'File "{self.__file_path}", line {line_number}'
        final_message += f'\n{" " * line_padding}{line}'
        if token is not None:
            line_start_index: int = sum(
                len(line) + 1 for line in self.__lines[: line_number - 1]
            )
            column_index: int = token.index - line_start_index - 1
            final_message += f'\n {" " * line_padding}{" " * column_index}^'
        final_message += f'\n{message_prefix} {message[0].lower() + message[1:]}'

        return final_message

    def _add_warning(self, token, message: str) -> None:
        final_message: str = self._get_exception_message(token, message, 'warning')
        self.__warnings.append(final_message)

    def _tokenized_attributes_to_dict(
        self,
        tokenized_attributes: list[tuple],
        attributesClass: Type[TermAttributes]
        | Type[FunctionAttributes]
        | Type[RelationshipAttributes],
    ) -> dict[str, Any]:
        allowed_attributes: list[str] = [
            field.name for field in fields(attributesClass)
        ]
        attributes: dict[str, str] = {}

        for attribute_pair in tokenized_attributes:
            if attribute_pair[0].value not in allowed_attributes:
                raise ValueError(
                    self._get_exception_message(
                        attribute_pair[0],
                        f'Unexpected attribute {attribute_pair[0].value}. One of the following was expected: {", ".join(allowed_attributes)}',
                        'error',
                    )
                )
            attributes[attribute_pair[0].value] = attribute_pair[1].value

        return attributes

    @_('statement_list')
    def program(self, p) -> Ontology:
        if not self.__ontology.meta.date:
            self.__ontology.meta.date = datetime.today().strftime('%Y-%m-%d')
        return self.__ontology

    @_('statement_list statement', '')
    def statement_list(self, p) -> None:
        pass

    @_('statement')
    def statement_list(self, p) -> None:
        pass

    @_('IDENTIFIER COLON STRING NEWLINE')
    def statement(self, p) -> None:
        allowed_meta_tags = [field.name for field in fields(Meta)]

        if p.IDENTIFIER not in allowed_meta_tags:
            raise ValueError(
                self._get_exception_message(
                    p._slice[0],
                    f'Unexpected meta tag. One of the following was expected: {", ".join(allowed_meta_tags)}',
                    'error',
                )
            )

        if not p.STRING:
            self._add_warning(p._slice[1], 'Version value is empty')

        setattr(self.__ontology.meta, p.IDENTIFIER, p.STRING)

    @_('TYPES_BLOCK COLON NEWLINE type_list')
    def statement(self, p) -> None:
        pass

    @_(
        'type_list type NEWLINE',
        'NEWLINE type_list',
        '',
    )
    def type_list(self, p) -> None:
        pass

    @_('IDENTIFIER COLON STRING COMMA STRING attributes')
    def type(self, p) -> None:
        existing_definition: Optional[Term | Function | Relationship] = (
            self.__ontology.find_definition_by_name(p.IDENTIFIER)
        )

        if existing_definition is not None:
            raise ValueError(
                self._get_exception_message(
                    p._slice[0],
                    f'Definition {p.IDENTIFIER} has already been declared',
                    'error',
                )
            )

        attributes: dict[str, Any] = self._tokenized_attributes_to_dict(
            p.attributes, TermAttributes
        )

        term = Term(
            name=p.IDENTIFIER,
            label=p.STRING0,
            description=p.STRING1,
            attributes=TermAttributes(**attributes),
        )

        if not p.STRING0:
            self._add_warning(p._slice[2], 'Term label is empty')

        if not p.STRING1:
            self._add_warning(p._slice[4], 'Term description is empty')

        self.__ontology.add_type(term)

    @_('FUNCTIONS_BLOCK COLON NEWLINE function_list')
    def statement(self, p) -> None:
        pass

    @_(
        'function_list function NEWLINE',
        'NEWLINE function_list',
        '',
    )
    def function_list(self, p) -> None:
        pass

    def _tokenized_function_attributes_to_dict(
        self,
        tokenized_attributes: list[tuple],
    ) -> dict[str, Any]:
        attributes: dict[str, Any] = self._tokenized_attributes_to_dict(
            tokenized_attributes, FunctionAttributes
        )

        if 'type' in attributes:
            attributes['type'] = RelationshipType.from_str(attributes['type'])
            if attributes['type'] is None:
                for key_token, value_token in tokenized_attributes:
                    if key_token.value == 'type':
                        raise ValueError(
                            self._get_exception_message(
                                value_token,
                                f'Unexpected type type. One of the following was expected: {", ".join(member.value for member in RelationshipType)}',
                                'error',
                            )
                        )

        return attributes

    @_('IDENTIFIER COLON STRING params ARROW IDENTIFIER COLON STRING attributes')
    def function(self, p) -> None:
        existing_definition: Optional[Term | Function | Relationship] = (
            self.__ontology.find_definition_by_name(p.IDENTIFIER0)
        )

        if existing_definition is not None:
            raise ValueError(
                self._get_exception_message(
                    p._slice[0],
                    f'Definition {p.IDENTIFIER0} has already been declared',
                    'error',
                )
            )

        input_types = p.params

        output_term: Optional[Term] = self.__ontology.find_term_by_name(p.IDENTIFIER1)

        if output_term is None:
            raise ValueError(
                self._get_exception_message(
                    p._slice[5], f'Undefined term {p.IDENTIFIER1}', 'error'
                )
            )

        output_type: FunctionArgument = FunctionArgument(output_term, p.STRING1)

        attributes: dict[str, Any] = self._tokenized_function_attributes_to_dict(
            p.attributes
        )

        function: Function = Function(
            name=p.IDENTIFIER0,
            label=p.STRING0,
            input_types=input_types,
            output_type=output_type,
            attributes=FunctionAttributes(**attributes),
        )

        if not p.STRING0:
            self._add_warning(p._slice[2], 'Label is empty')

        if not p.STRING1:
            self._add_warning(p._slice[7], 'Output term label is empty')

        self.__ontology.add_function(function)

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

            term: Optional[Term] = self.__ontology.find_term_by_name(term_name)

            if term is None:
                raise ValueError(
                    self._get_exception_message(
                        term_token, f'Undefined term {term_name}', 'error'
                    )
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

    @_('HIERARCHY_BLOCK COLON NEWLINE hierarchy_list')
    def statement(self, p) -> None:
        pass

    @_(
        'hierarchy_list relationship NEWLINE',
        'NEWLINE hierarchy_list',
        '',
    )
    def hierarchy_list(self, p) -> None:
        pass

    def _tokenized_relationship_attributes_to_dict(
        self,
        tokenized_attributes: list[tuple],
    ) -> dict[str, Any]:
        attributes: dict[str, Any] = self._tokenized_attributes_to_dict(
            tokenized_attributes, RelationshipAttributes
        )

        if 'direction' in attributes:
            attributes['direction'] = RelationshipDirection.from_str(
                attributes['direction']
            )
            if attributes['direction'] is None:
                for key_token, value_token in tokenized_attributes:
                    if key_token.value == 'direction':
                        raise ValueError(
                            self._get_exception_message(
                                value_token,
                                f'Unexpected direction type. One of the following was expected: {", ".join(member.value for member in RelationshipDirection)}',
                                'error',
                            )
                        )

        return attributes

    def _add_relationship(
        self,
        name_token,
        parent_token,
        relationship_type_token,
        child_token,
        attributes_tokens,
    ) -> None:
        if name_token is not None:
            existing_definition: Optional[Term | Function | Relationship] = (
                self.__ontology.find_definition_by_name(name_token.value)
            )
            if existing_definition is not None:
                raise ValueError(
                    self._get_exception_message(
                        name_token,
                        f'Definition {name_token.value} has already been declared',
                        'error',
                    )
                )

        parent: Optional[Term] = self.__ontology.find_term_by_name(parent_token.value)

        if parent is None:
            raise ValueError(
                self._get_exception_message(
                    parent_token, f'Undefined term {parent_token.value}', 'error'
                )
            )

        relationship_type: Optional[RelationshipType] = RelationshipType.from_str(
            relationship_type_token.value
        )

        if relationship_type is None:
            raise ValueError(
                self._get_exception_message(
                    relationship_type_token,
                    f'Unexpected relationship type. One of the following was expected: {", ".join(member.value for member in RelationshipType)}',
                    'error',
                )
            )

        child: Optional[Term] = self.__ontology.find_term_by_name(child_token.value)

        if child is None:
            raise ValueError(
                self._get_exception_message(
                    child_token, f'Undefined term {child_token.value}', 'error'
                )
            )

        children: list[Term] = [child]

        attributes: dict[str, Any] = self._tokenized_relationship_attributes_to_dict(
            attributes_tokens
        )

        relationship: Relationship = Relationship(
            name=name_token.value if name_token else None,
            parent=parent,
            relationship=relationship_type,
            children=children,
            attributes=RelationshipAttributes(**attributes),
        )
        self.__ontology.add_relationship(relationship)

    @_('IDENTIFIER IDENTIFIER IDENTIFIER attributes')
    def relationship(self, p) -> None:
        self._add_relationship(
            None,
            p._slice[0],
            p._slice[1],
            p._slice[2],
            p.attributes,
        )

    @_('IDENTIFIER COLON IDENTIFIER IDENTIFIER IDENTIFIER attributes')
    def relationship(self, p) -> None:
        self._add_relationship(
            p._slice[0],
            p._slice[2],
            p._slice[3],
            p._slice[4],
            p.attributes,
        )

    @_('FIGURE_BLOCK STRING COLON NEWLINE figure_list')
    def statement(self, p) -> None:
        figure: Figure = Figure(name=p.STRING)

        for token in p.figure_list:
            definition: Optional[Term | Function | Relationship] = (
                self.__ontology.find_definition_by_name(token.value)
            )
            if definition is None:
                raise ValueError(
                    self._get_exception_message(
                        token,
                        f'Undefined identifier {token.value}',
                        'error',
                    )
                )
            if isinstance(definition, Term):
                figure.types.append(definition)
            elif isinstance(definition, Function):
                figure.functions.append(definition)
            elif isinstance(definition, Relationship):
                figure.hierarchy.append(definition)

        self.__ontology.add_figure(figure)

    @_('figure_list IDENTIFIER NEWLINE')
    def figure_list(self, p) -> None:
        return p.figure_list + [p._slice[1]]

    @_(
        'NEWLINE figure_list',
    )
    def figure_list(self, p) -> None:
        return p.figure_list

    @_('')
    def figure_list(self, p) -> list:
        return []

    @_(
        'COMMA LBRACE attribute_list RBRACE',
        'COMMA LBRACE NEWLINE attribute_list RBRACE',
        'COMMA LBRACE attribute_list NEWLINE RBRACE',
        'COMMA LBRACE NEWLINE attribute_list NEWLINE RBRACE',
        'COMMA LBRACE NEWLINE attribute_list COMMA NEWLINE RBRACE',
    )
    def attributes(self, p) -> list[tuple]:
        return p.attribute_list

    @_('')
    def attributes(self, p) -> list[tuple]:
        return []

    @_(
        'attribute_list COMMA attribute',
        'attribute_list COMMA NEWLINE attribute',
    )
    def attribute_list(self, p) -> list[tuple]:
        return p.attribute_list + [p.attribute]

    @_('attribute')
    def attribute_list(self, p) -> list[tuple]:
        return [p.attribute]

    @_('')
    def attribute_list(self, p) -> list[tuple]:
        return []

    @_('IDENTIFIER COLON STRING')
    def attribute(self, p) -> tuple:
        if not p.STRING:
            self._add_warning(p._slice[2], 'Attribute value is empty')

        return (p._slice[0], p._slice[2])

    @_('NEWLINE')
    def statement(self, p) -> None:
        pass

    def error(self, p) -> None:
        if p:
            raise SyntaxError(
                self._get_exception_message(
                    p,
                    f'Syntax error ({p.type})',
                    'error',
                )
            )

        raise SyntaxError(f'{constants.error_prefix} Syntax error at EOF')
