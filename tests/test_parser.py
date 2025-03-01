import json
import pprint
from dataclasses import asdict

from ontol.oast import TypeDict
from src.ontol import Parser, Term, Function, Relationship

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
    assert ontology.meta.date_created is not None
    assert len(ontology.types) == 0
    assert len(ontology.functions) == 0
    assert len(ontology.hierarchy) == 0
    assert len(warnings) == 0


def test_parse_commented_file(parser):
    content: str = """
    # version: '1.0'
    # title: 'Basic linear algebra'
    # author: 'Firstname Lastname'
    # desc: 'Matrices'

    # types:
    # number: 'Number', ''
    # matrix: 'Matrix', ''

    # functions:
    # transpose: 'Transpose' (matrix) -> matrix: 'Transposed matrix'

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


def test_parse_type_with_incorrect_arguments(parser):
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
    descartes: 'Cartesian product' (set: 'First set', set: 'Second set') -> set: 'Result set', { color: '#fff }
    """
    ontology, warnings = parser.parse(content, 'test.ontol')

    assert len(ontology.functions) == 1

    func: Function = ontology.functions[0]
    assert func.name == 'descartes'
    assert func.label == 'Cartesian product'
    assert func.input_types[0]['name'].name == 'set'
    assert func.input_types[0]['name'].label == 'Множество'
    assert func.input_types[0]['name'].description == 'Коллекция уникальных элементов'
    assert func.input_types[0]['label'] == 'First set'
    assert func.input_types[1]['name'].name == 'set'
    assert func.input_types[1]['name'].label == 'Множество'
    assert func.input_types[1]['name'].description == 'Коллекция уникальных элементов'
    assert func.input_types[1]['label'] == 'Second set'
    assert func.output_type['name'].name == 'set'
    assert func.output_type['name'].label == 'Множество'
    assert func.output_type['name'].description == 'Коллекция уникальных элементов'
    assert func.output_type['label'] == 'Result set'
    assert func.attributes == {'color': '#fff'}
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
    assert func.input_types[0]['name'].name == 'number'
    assert func.input_types[0]['name'].label == 'Число'
    assert func.input_types[0]['name'].description == 'Число'
    assert func.input_types[0]['label'] == 'Dividend'
    assert func.input_types[1]['name'].name == 'number'
    assert func.input_types[1]['name'].label == 'Число'
    assert func.input_types[1]['name'].description == 'Число'
    assert func.input_types[1]['label'] == 'Divisor'
    assert func.output_type['name'].name == 'number'
    assert func.output_type['name'].label == 'Число'
    assert func.output_type['name'].description == 'Число'
    assert func.output_type['label'] == 'Quotient'
    assert func.attributes == {}
    assert len(warnings) == 0


def test_parse_function_with_missing_output(parser):
    content = """
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
    date: 'Current date', 'Current date'
    functions:
    today: 'Returns current date' () -> date: 'Current date'
    """
    ontology, warnings = parser.parse(content, 'test.ontol')

    assert len(ontology.functions) == 1

    func: Function = ontology.functions[0]
    assert func.name == 'today'
    assert func.label == 'Returns current date'
    assert func.input_types == []
    assert func.output_type['name'].name == 'date'
    assert func.output_type['label'] == 'Current date'
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
    assert func.input_types[0]['name'].name == 'set'
    assert func.input_types[0]['label'] == ''
    assert func.input_types[1]['name'].name == 'set'
    assert func.input_types[1]['label'] == ''
    assert func.output_type['name'].name == 'set'
    assert func.output_type['label'] == ''
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
    assert len(warnings) == 4


def test_parse_meta(parser):
    content = """
    version: '1.0'
    title: "Basic calculus" # can we come up with a more interesting name?
    author: 'Firstname Lastname'
    desc: "Limits, differentiation and integrals"
    type: 'Базовый'
    """
    ontology, warnings = parser.parse(content, 'test.ontol')

    assert ontology.meta is not None
    assert ontology.meta.version == '1.0'
    assert ontology.meta.title == 'Basic calculus'
    assert ontology.meta.author == 'Firstname Lastname'
    assert ontology.meta.description == 'Limits, differentiation and integrals'
    assert ontology.meta.type == 'Базовый'
    assert len(warnings) == 0


def test_parse_meta_without_qoutes(parser):
    content = """
    version: 1.0
    title: "Basic calculus"
    author: 'Firstname Lastname'
    desc: "Limits, differentiation and integrals"
    """
    with pytest.raises(SyntaxError):
        parser.parse(content, 'test.ontol')


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
