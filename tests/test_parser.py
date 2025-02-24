from src.ontol import Parser, Term, Function, Relationship

import pytest


@pytest.fixture
def parser():
    return Parser()


def test_parse_empty_file(parser):
    content: str = ''
    ontology, warnings = parser.parse(content, 'test.ontol')
    assert ontology.meta.version is None
    assert ontology.meta.name is None
    assert ontology.meta.author is None
    assert ontology.meta.description is None
    assert ontology.meta.type is None
    assert ontology.meta.date_created is not None
    assert len(ontology.types) == 0
    assert len(ontology.functions) == 0
    assert len(ontology.hierarchy) == 0
    assert len(warnings) == 0


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
    assert term.attributes == {'color': '#ffffff'}


def test_parse_type_without_arguments(parser):
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
    assert term.attributes == {}
    assert len(warnings) == 0


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
    assert term.attributes == {}
    assert len(warnings) == 2


def test_parse_type_without_label_and_desc(parser):
    content: str = """
    types:
    set: ''
    """
    with pytest.raises(SyntaxError):
        ontology, warnings = parser.parse(content, 'test.ontol')

    content: str = """
    types:
    set
    """
    with pytest.raises(SyntaxError):
        ontology, warnings = parser.parse(content, 'test.ontol')


def test_parse_function(parser):
    content = """
    functions:
    descartes: 'Cartesian product' (set: 'First set', set: 'Second set') -> set: 'Result set', { color: '#fff }
    """
    ontology, warnings = parser.parse(content, 'test.ontol')

    assert len(ontology.functions) == 1

    func: Function = ontology.functions[0]
    assert func.name == 'descartes'
    assert func.label == 'Cartesian product'
    assert func.input_types == [('set', 'First set'), ('set', 'Second set')]
    assert func.output_type == ('set', 'Result set')
    assert func.attributes == {'color': '#fff'}
    assert len(warnings) == 0


def test_parse_function_with_empty_attributes(parser):
    content = """
    functions:
    divide: 'Divide two numbers' (number: 'Dividend', number: 'Divisor') -> number: 'Quotient', {}
    """
    ontology, warnings = parser.parse(content, 'test.ontol')

    assert len(ontology.functions) == 1

    func: Function = ontology.functions[0]
    assert func.name == 'divide'
    assert func.label == 'Divide two numbers'
    assert func.input_types == [('number', 'Dividend'), ('number', 'Divisor')]
    assert func.output_type == ('number', 'Quotient')
    assert func.attributes == {}
    assert len(warnings) == 0


def test_parse_function_with_missing_output(parser):
    content = """
    functions:
    add: 'Addition' (number: 'First number', number: 'Second number') -> , {color: '#fff'}
    """
    with pytest.raises(SyntaxError):
        ontology, warnings = parser.parse(content, 'test.ontol')


def test_parse_function_without_arguments(parser):
    content = """
    functions:
    today: 'Returns current date' () -> date: 'Current date'
    """
    ontology, warnings = parser.parse(content, 'test.ontol')

    assert len(ontology.functions) == 1

    func: Function = ontology.functions[0]
    assert func.name == 'today'
    assert func.label == 'Returns current date'
    assert func.input_types == []
    assert func.output_type == ('date', 'Current date')
    assert len(warnings) == 0


def test_parse_with_empty_labels(parser):
    content = """
    functions:
    descartes: '' (set: '', set: '') -> set: ''
    """
    ontology, warnings = parser.parse(content, 'test.ontol')

    assert len(ontology.functions) == 1

    func: Function = ontology.functions[0]
    assert func.name == 'descartes'
    assert func.label == ''
    assert func.input_types == [('set', ''), ('set', '')]
    assert func.output_type == ('set', '')
    assert len(warnings) == 4


def test_parse_heierarchy(parser):
    content = """
    hierarchy:
    element inheritance set
    """
    ontology, warnings = parser.parse(content, 'test.ontol')

    assert len(ontology.hierarchy) == 1

    rel: Relationship = ontology.hierarchy[0]
    assert rel.parent == 'element'
    assert rel.relationship == 'inheritance'
    assert rel.child == ['set']
    assert len(warnings) == 0


def test_parse_meta(parser):
    content = """
    version: '1.0'
    title: 'Basic calculus' # can we come up with a more interesting name?
    author: 'Firstname Lastname'
    desc: 'Limits, differentiation and integrals'
    type: 'Базовый'
    """
    ontology, warnings = parser.parse(content, 'test.ontol')

    assert ontology.meta is not None
    assert ontology.meta.version == '1.0'
    assert ontology.meta.name == 'Basic calculus'
    assert ontology.meta.author == 'Firstname Lastname'
    assert ontology.meta.description == 'Limits, differentiation and integrals'
    assert ontology.meta.type == 'Базовый'
    assert len(warnings) == 0


def test_combined_parsing(parser):
    content = """
    # Ontology information
    version: '1.0'
    title: 'Basic linear algebra'

    # Types we have
    types:
    number: 'Number', 'Some real number from R field'

    # Other type
    types:
    matrix: 'Matrix', 'Rectangular array or table of numbers'

    # Functions we have
    functions:
    # Describe more functions
    transpose: 'Transpose' (matrix) -> matrix: 'Transposed matrix'

    # And relations we have
    hierarchy:
    matrix composition number
    """
    ontology, warnings = parser.parse(content, 'test.ontol')

    assert len(ontology.types) == 2
    assert len(ontology.functions) == 1
    assert len(ontology.hierarchy) == 1

    assert ontology.meta is not None

    assert len(warnings) == 0
