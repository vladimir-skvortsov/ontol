from src.ontol import Function, Meta, Ontology, Relationship, Term, PlantUML

import pytest


@pytest.fixture
def mock_ontology():
    ontology = Ontology()
    ontology.set_meta(
        Meta(
            version='1.0',
            name='TestOntology',
            author='Author',
            description='Test ontology',
            type='Базовый',
            date_created='2024-01-01',
        )
    )
    ontology.add_type(Term(name='MyType', description='A test type'))
    ontology.add_function(
        Function(
            name='MyFunction',
            input_types=['int', 'str'],
            output_types=['bool'],
            description='Test function',
        )
    )
    ontology.add_relationship(Relationship(expression='A > B'))
    return ontology


@pytest.fixture
def generator():
    return PlantUML()


def test_generate_full_uml(generator, mock_ontology):
    uml_output = generator.generate(mock_ontology)
    assert '@startuml' in uml_output
    assert '@enduml' in uml_output
    assert 'title TestOntology by Author' in uml_output
    assert 'class MyType {\n  A test type\n}' in uml_output
    assert 'class MyFunction <<Function>> {' in uml_output
    assert '+MyFunction(int, str) : (bool)' in uml_output
    assert 'note "A > B" as N' in uml_output


def test_generate_type(generator):
    term = Term(name='MyType', description='A test type')
    result = generator._generate_type(term)
    assert result == 'class MyType {\n  A test type\n}'


def test_generate_function(generator):
    func = Function(
        name='MyFunction',
        input_types=['int'],
        output_types=['bool'],
        description='Test function',
    )
    result = generator._generate_function(func)
    assert 'class MyFunction <<Function>> {' in result
    assert '+MyFunction(int) : (bool)' in result
    assert 'Test function' in result


def test_generate_logical_expression(generator):
    relation = Relationship(expression='A > B')
    result = generator._generate_logical_expression(relation)
    assert 'note "A > B" as N' in result
