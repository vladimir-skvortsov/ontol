from ontol import (
    Parser,
    Term,
    Function,
    Relationship,
    TermAttributes,
    FunctionAttributes,
    RelationshipAttributes,
)

import pytest


@pytest.fixture
def parser():
    return Parser()


def test_parse_empty_file(parser):
    content: str = ''
    ontology, warnings = parser.parse(content, 'test.ontol')
    assert ontology.meta.version is None
    assert ontology.meta.title is None
    assert ontology.meta.author is None
    assert ontology.meta.description is None
    assert ontology.meta.type is None
    assert ontology.meta.date is not None
    assert len(ontology.types) == 0
    assert len(ontology.functions) == 0
    assert len(ontology.hierarchy) == 0
    assert len(warnings) == 0


def test_parse_commented_file(parser):
    content: str = """
    # version: '1.0'
    # title: 'Basic linear algebra'
    # author: 'Firstname Lastname'
    # description: 'Matrices'

    # types:
    # number: 'Number', ''
    # matrix: 'Matrix', ''

    # functions:
    # transpose: 'Transpose' (matrix: '') -> matrix: 'Transposed matrix'

    # hierarchy:
    # matrix composition number
    """
    ontology, warnings = parser.parse(content, 'test.ontol')

    assert ontology.meta.version is None
    assert ontology.meta.title is None
    assert ontology.meta.author is None
    assert ontology.meta.description is None
    assert len(ontology.types) == 0
    assert len(ontology.functions) == 0
    assert len(ontology.hierarchy) == 0
    assert len(warnings) == 0


def test_parse_meta_tags(parser):
    content: str = """
    version: '2.5.5'
    title: 'Biology'
    author: 'Firstname Lastname'
    description: 'Biology for high school'
    date: '02.02.2025'
    """
    ontology, warnings = parser.parse(content, 'test.ontol')

    assert len(ontology.types) == 0
    assert len(ontology.functions) == 0
    assert len(ontology.hierarchy) == 0

    assert ontology.meta is not None

    assert ontology.meta.version == '2.5.5'
    assert ontology.meta.title == 'Biology'
    assert ontology.meta.author == 'Firstname Lastname'
    assert ontology.meta.description == 'Biology for high school'
    assert ontology.meta.date == '02.02.2025'


def test_parse_empty_meta_tags(parser):
    content: str = """
    version: ''
    title: ''
    author: ''
    description: ''
    date: ''
    """
    ontology, warnings = parser.parse(content, 'test.ontol')

    assert len(ontology.types) == 0
    assert len(ontology.functions) == 0
    assert len(ontology.hierarchy) == 0

    assert ontology.meta is not None

    assert ontology.meta.version == ''
    assert ontology.meta.title == ''
    assert ontology.meta.author == ''
    assert ontology.meta.description == ''
    assert ontology.meta.date != ''


def test_parse_file_without_meta_tags(parser):
    content: str = """
    types:
    set: 'Множество', 'Коллекция уникальных элементов', {color: '#ffffff'}
    """
    ontology, warnings = parser.parse(content, 'test.ontol')

    assert len(ontology.types) == 1
    assert len(ontology.functions) == 0
    assert len(ontology.hierarchy) == 0

    assert ontology.meta is not None

    assert ontology.meta.version is None
    assert ontology.meta.title is None
    assert ontology.meta.author is None
    assert ontology.meta.description is None
    assert ontology.meta.date is not None


def test_parse_file_with_incorrect_meta_tags(parser):
    content: str = """
    university: 'Peter the Great St.Petersburg Polytechnic University'
    """
    with pytest.raises(ValueError):
        parser.parse(content, 'test.ontol')

    content: str = """
    version: 1.0.0
    """
    with pytest.raises(SyntaxError):
        parser.parse(content, 'test.ontol')
        parser.parse(content, 'test.ontol')

    content: str = """
    version '1.0.0'
    """
    with pytest.raises(SyntaxError):
        parser.parse(content, 'test.ontol')

    content: str = """
    'version': '1.0.0'
    """
    with pytest.raises(SyntaxError):
        parser.parse(content, 'test.ontol')

    content: str = """
    'version' '1.0.0'
    """
    with pytest.raises(SyntaxError):
        parser.parse(content, 'test.ontol')


def test_parse_type(parser):
    content: str = """
    types:
    set: 'Множество', 'Коллекция уникальных элементов', {color: '#ffffff'}
    """
    ontology, warnings = parser.parse(content, 'test.ontol')

    assert len(ontology.types) == 1

    term: Term = ontology.types[0]
    assert term.name == 'set'
    assert term.label == 'Множество'
    assert term.description == 'Коллекция уникальных элементов'
    assert term.attributes == TermAttributes(color='#ffffff')


def test_parse_type_Wth_multiline_attributes(parser):
    content: str = """
    types:
    set: 'Множество', 'Коллекция уникальных элементов', {
        color: '#ffffff'
    }
    """
    ontology, warnings = parser.parse(content, 'test.ontol')

    assert len(ontology.types) == 1

    term: Term = ontology.types[0]
    assert term.name == 'set'
    assert term.label == 'Множество'
    assert term.description == 'Коллекция уникальных элементов'
    assert term.attributes == TermAttributes(color='#ffffff')


def test_parse_type_Wth_multiline_attributes_with_trailing_comma(parser):
    content: str = """
    types:
    set: 'Множество', 'Коллекция уникальных элементов', {
        color: '#ffffff',
    }
    """
    ontology, warnings = parser.parse(content, 'test.ontol')

    assert len(ontology.types) == 1

    term: Term = ontology.types[0]
    assert term.name == 'set'
    assert term.label == 'Множество'
    assert term.description == 'Коллекция уникальных элементов'
    assert term.attributes == TermAttributes(color='#ffffff')


def test_parse_type_without_attributes(parser):
    content: str = """
    types:
    set: 'Множество', 'Коллекция уникальных элементов'
    """
    ontology, warnings = parser.parse(content, 'test.ontol')

    assert len(ontology.types) == 1

    term: Term = ontology.types[0]
    assert term.name == 'set'
    assert term.label == 'Множество'
    assert term.description == 'Коллекция уникальных элементов'
    assert term.attributes == TermAttributes()
    assert len(warnings) == 0


def test_parse_type_with_empty_attributes(parser):
    content: str = """
    types:
    set: 'Множество', 'Коллекция уникальных элементов', {}
    """
    ontology, warnings = parser.parse(content, 'test.ontol')

    assert len(ontology.types) == 1

    term: Term = ontology.types[0]
    assert term.name == 'set'
    assert term.label == 'Множество'
    assert term.description == 'Коллекция уникальных элементов'
    assert term.attributes == TermAttributes()
    assert len(warnings) == 0


def test_parse_type_with_incorrect_attributes(parser):
    content: str = """
    types:
    set: 'Множество', 'Коллекция уникальных элементов', { foo }
    """
    with pytest.raises(SyntaxError):
        parser.parse(content, 'test.ontol')

    content: str = """
    types:
    set: 'Множество', 'Коллекция уникальных элементов', { foo, bar, baz }
    """
    with pytest.raises(SyntaxError):
        parser.parse(content, 'test.ontol')

    content: str = """
    types:
    set: 'Множество', 'Коллекция уникальных элементов', { foo bar }
    """
    with pytest.raises(SyntaxError):
        parser.parse(content, 'test.ontol')

    content: str = """
    types:
    set: 'Множество', 'Коллекция уникальных элементов', { 123 }
    """
    with pytest.raises(SyntaxError):
        parser.parse(content, 'test.ontol')

    content: str = """
    types:
    set: 'Множество', 'Коллекция уникальных элементов' { color: '#red' }
    """
    with pytest.raises(SyntaxError):
        parser.parse(content, 'test.ontol')

    content: str = """
    types:
    set: 'Множество', 'Коллекция уникальных элементов', { 'color': '#red' }
    """
    with pytest.raises(SyntaxError):
        parser.parse(content, 'test.ontol')

    content: str = """
    types:
    set: 'Множество', 'Коллекция уникальных элементов', { color: red }
    """
    with pytest.raises(SyntaxError):
        parser.parse(content, 'test.ontol')


def test_parse_type_with_empty_label_and_desc(parser):
    content: str = """
    types:
    set: '', ''
    """
    ontology, warnings = parser.parse(content, 'test.ontol')

    assert len(ontology.types) == 1

    term: Term = ontology.types[0]
    assert term.name == 'set'
    assert term.label == ''
    assert term.description == ''
    assert term.attributes == TermAttributes()
    assert len(warnings) == 2


def test_parse_type_without_label_and_desc(parser):
    content: str = """
    types:
    set: ''
    """
    with pytest.raises(SyntaxError):
        parser.parse(content, 'test.ontol')

    content: str = """
    types:
    set
    """
    with pytest.raises(SyntaxError):
        parser.parse(content, 'test.ontol')


def test_parse_function(parser):
    content = """
    types:
    set: 'Множество', 'Коллекция уникальных элементов'
    functions:
    descartes: 'Cartesian product' (set: 'First set', set: 'Second set') -> set: 'Result set', { color: '#fff' }
    """
    ontology, warnings = parser.parse(content, 'test.ontol')

    assert len(ontology.functions) == 1

    func: Function = ontology.functions[0]
    assert func.name == 'descartes'
    assert func.label == 'Cartesian product'
    assert func.input_types[0].term.name == 'set'
    assert func.input_types[0].term.label == 'Множество'
    assert func.input_types[0].term.description == 'Коллекция уникальных элементов'
    assert func.input_types[0].label == 'First set'
    assert func.input_types[1].term.name == 'set'
    assert func.input_types[1].term.label == 'Множество'
    assert func.input_types[1].term.description == 'Коллекция уникальных элементов'
    assert func.input_types[1].label == 'Second set'
    assert func.output_type.term.name == 'set'
    assert func.output_type.term.label == 'Множество'
    assert func.output_type.term.description == 'Коллекция уникальных элементов'
    assert func.output_type.label == 'Result set'
    assert func.attributes == FunctionAttributes(color='#fff')
    assert len(warnings) == 0


def test_parse_function_with_empty_attributes(parser):
    content = """
    types:
    number: 'Число', 'Число'
    functions:
    divide: 'Divide two numbers' (number: 'Dividend', number: 'Divisor') -> number: 'Quotient', {}
    """
    ontology, warnings = parser.parse(content, 'test.ontol')

    assert len(ontology.functions) == 1

    func: Function = ontology.functions[0]
    assert func.name == 'divide'
    assert func.label == 'Divide two numbers'
    assert func.input_types[0].term.name == 'number'
    assert func.input_types[0].term.label == 'Число'
    assert func.input_types[0].term.description == 'Число'
    assert func.input_types[0].label == 'Dividend'
    assert func.input_types[1].term.name == 'number'
    assert func.input_types[1].term.label == 'Число'
    assert func.input_types[1].term.description == 'Число'
    assert func.input_types[1].label == 'Divisor'
    assert func.output_type.term.name == 'number'
    assert func.output_type.term.label == 'Число'
    assert func.output_type.term.description == 'Число'
    assert func.output_type.label == 'Quotient'
    assert func.attributes == FunctionAttributes()
    assert len(warnings) == 0


def test_parse_function_with_missing_output(parser):
    content = """
    types:
    number: '', ''
    functions:
    add: 'Addition' (number: 'First number', number: 'Second number') -> , {color: '#fff'}
    """
    with pytest.raises(SyntaxError):
        parser.parse(content, 'test.ontol')


def test_parse_function_with_missing_label(parser):
    content = """
    functions:
    add(number: 'First number', number: 'Second number') -> number: 'Result', {color: '#fff'}
    """
    with pytest.raises(SyntaxError):
        parser.parse(content, 'test.ontol')


def test_parse_function_without_arguments(parser):
    content = """
    types:
    time: 'Current time', 'Current time'
    functions:
    now: 'Returns current time' () -> time: 'Current time'
    """
    ontology, warnings = parser.parse(content, 'test.ontol')

    assert len(ontology.functions) == 1

    func: Function = ontology.functions[0]
    assert func.name == 'now'
    assert func.label == 'Returns current time'
    assert func.input_types == []
    assert func.output_type.term.name == 'time'
    assert func.output_type.label == 'Current time'
    assert len(warnings) == 0


def test_parse_with_empty_labels(parser):
    content = """
    types:
    set: '', ''
    functions:
    descartes: '' (set: '', set: '') -> set: ''
    """
    ontology, warnings = parser.parse(content, 'test.ontol')

    assert len(ontology.functions) == 1

    func: Function = ontology.functions[0]
    assert func.name == 'descartes'
    assert func.label == ''
    assert func.input_types[0].term.name == 'set'
    assert func.input_types[0].label == ''
    assert func.input_types[1].term.name == 'set'
    assert func.input_types[1].label == ''
    assert func.output_type.term.name == 'set'
    assert func.output_type.label == ''
    print('\n\n'.join(warnings))
    assert len(warnings) == 6


def test_parse_heierarchy(parser):
    content = """
    types:
    set: '', ''
    element: '', ''
    hierarchy:
    element inheritance set
    """
    ontology, warnings = parser.parse(content, 'test.ontol')

    assert len(ontology.hierarchy) == 1

    rel: Relationship = ontology.hierarchy[0]
    assert rel.parent.name == 'element'
    assert rel.relationship.value == 'inheritance'
    assert rel.children[0].name == 'set'
    assert rel.attributes == RelationshipAttributes()
    assert len(warnings) == 4


def test_parse_heierarchy_with_attributes(parser):
    content = """
    types:
    set: '', ''
    element: '', ''
    hierarchy:
    element inheritance set, { color: '#red' }
    """
    ontology, warnings = parser.parse(content, 'test.ontol')

    assert len(ontology.hierarchy) == 1

    rel: Relationship = ontology.hierarchy[0]
    assert rel.parent.name == 'element'
    assert rel.relationship.value == 'inheritance'
    assert rel.children[0].name == 'set'
    assert rel.attributes == RelationshipAttributes(color='#red')
    assert len(warnings) == 4


def test_parse_heierarchy_with_multiline_attributes(parser):
    content = """
    types:
    set: '', ''
    element: '', ''
    hierarchy:
    element inheritance set, {
        color: '#red'
    }
    """
    ontology, warnings = parser.parse(content, 'test.ontol')

    assert len(ontology.hierarchy) == 1

    rel: Relationship = ontology.hierarchy[0]
    assert rel.parent.name == 'element'
    assert rel.relationship.value == 'inheritance'
    assert rel.children[0].name == 'set'
    assert rel.attributes == RelationshipAttributes(color='#red')
    assert len(warnings) == 4


def test_parse_heierarchy_with_empty_attributes(parser):
    content = """
    types:
    set: '', ''
    element: '', ''
    hierarchy:
    element inheritance set, {  }
    """
    ontology, warnings = parser.parse(content, 'test.ontol')

    assert len(ontology.hierarchy) == 1

    rel: Relationship = ontology.hierarchy[0]
    assert rel.parent.name == 'element'
    assert rel.relationship.value == 'inheritance'
    assert len(rel.children) == 1
    assert rel.children[0].name == 'set'
    assert rel.attributes == RelationshipAttributes()
    assert len(warnings) == 4


def test_parse_heierarchy_unexpected_relationship(parser):
    content = """
    types:
    set: '', ''
    element: '', ''
    hierarchy:
    element loves set, {  }
    """
    with pytest.raises(ValueError):
        parser.parse(content, 'test.ontol')


def test_parse_heierarchy_with_undefined_types(parser):
    content = """
    types:
    set: '', ''
    hierarchy:
    element composition set
    """
    with pytest.raises(ValueError):
        parser.parse(content, 'test.ontol')

    content = """
    types:
    set: '', ''
    hierarchy:
    set composition element
    """
    with pytest.raises(ValueError):
        parser.parse(content, 'test.ontol')

    content = """
    types:
    set: '', ''
    hierarchy:
    element composition element
    """
    with pytest.raises(ValueError):
        parser.parse(content, 'test.ontol')


def test_combined_parsing(parser):
    content = """
    # Ontology information
    version: '1.0'
    title: 'Basic linear algebra'

    # Types we have
    types:
    # todo: Add laso complex numbers
    number: 'Number', 'Some real number from R field'

    # Other type
    types:
    matrix: 'Matrix', 'Rectangular array or table of numbers'

    # Functions we have
    functions:
    # Describe more functions
    transpose: 'Transpose' (matrix: 'Initial matrix') -> matrix: 'Transposed matrix'

    # And relations we have
    hierarchy:
    # All also vectors
    matrix composition number
    """
    ontology, warnings = parser.parse(content, 'test.ontol')

    assert len(ontology.types) == 2
    assert len(ontology.functions) == 1
    assert len(ontology.hierarchy) == 1

    assert ontology.meta is not None

    assert len(warnings) == 0
