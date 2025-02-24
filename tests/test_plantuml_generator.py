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
    # TODO: add term without color attribute
    ontology.add_type(Term(name='MyTypeParent', label='test label', description='A test type',
                           attributes={'color': '#E6B8B7'}))
    ontology.add_type(Term(name='MyTypeChild', label='test label', description='A test type',
                           attributes={'color': '#E6B8B7'}))
    ontology.add_function(
        Function(
            name='MyFunction',
            label='test label',
            input_types=[('int', 'test in1'), ('str', 'test in2')],
            output_type=('bool', 'test_type'),
            # attributes={'color': '#E6B8B7'}
        )
    )
    ontology.add_relationship(
        Relationship(
            parent='MyTypeParent',
            relationship='contains',
            child=['MyTypeChild'],
        )
    )
    return ontology


@pytest.fixture
def generator():
    return PlantUML()


def test_generate_full_uml(generator: PlantUML, mock_ontology):
    uml_output = generator.generate(mock_ontology)
    assert '@startuml' in uml_output
    assert '@enduml' in uml_output
    assert 'title TestOntology by Author' in uml_output
    # assert 'class MyTypeParent {\n  A test type\n}' in uml_output
    assert 'class MyTypeParent' in uml_output
    assert 'class MyTypeChild' in uml_output
    assert 'class MyFunction <<Function>> {' in uml_output
    # assert '+MyFunction(int, str) : (bool)' in uml_output
    assert 'contains' in uml_output


def test_generate_type(generator: PlantUML):
    term = Term(name='MyType', description='A test type',  label='test label')
    result = generator._generate_type(term)
    assert result == 'class MyType {\n  A test type\n}'


def test_generate_function(generator: PlantUML):
    func = Function(
        name='MyFunction',
        label='test label',
        input_types=[('int', 'test')],
        output_type=('bool', ""),
        attributes={'color': '#E6B8B7'}
    )
    result = generator._generate_function(func)
    assert 'class MyFunction <<Function>> {' in result
    assert '+MyFunction(int) : (bool)' in result
    assert 'Test function' in result


def test_generate_logical_expression(generator: PlantUML):
    relation = Relationship(
            parent='MyTypeParent',
            relationship='contains',
            child=['MyTypeChild'],
        )
    result = generator._generate_relationship(relation)
    assert 'note "A > B" as N' in result
