from ontol import (
    Function,
    Meta,
    Ontology,
    Relationship,
    Term,
    FunctionArgument,
    RelationshipType,
    TermAttributes,
    FunctionAttributes,
    Retranslator,
)

import pytest


@pytest.fixture
def mock_ontology():
    ontology = Ontology()
    ontology.set_meta(
        Meta(
            version='1.0',
            title='TestOntology',
            author='Author',
            description='Test ontology',
            type='Базовый',
            date='2024-01-01',
        )
    )
    ontology.add_type(
        Term(
            name='MyTypeParent',
            label='test label Term1',
            description='A test type1',
            attributes=TermAttributes(color='#E6B8B7'),
        )
    )
    ontology.add_type(
        Term(name='MyTypeChild', label='test label Term2', description='A test type2')
    )
    ontology.add_function(
        Function(
            name='MyFunction1',
            label='test label Func1',
            input_types=[
                FunctionArgument(Term('MyTypeChild'), 'test1 in1'),
                FunctionArgument(Term('MyTypeChild'), 'test1 in2'),
            ],
            output_type=FunctionArgument(Term('MyTypeParent'), 'test_type1'),
            attributes=FunctionAttributes(colorArrow='#E6B8B7'),
        )
    )
    ontology.add_relationship(
        Relationship(
            parent=Term('MyTypeParent'),
            relationship=RelationshipType.COMPOSITION,
            children=[Term('MyTypeChild')],
        )
    )
    return ontology


@pytest.fixture
def retranslator():
    return Retranslator()


def test_translate_full_ontology(retranslator: Retranslator, mock_ontology):
    retr_output = retranslator.translate(mock_ontology)
    assert "version: '1.0'" in retr_output
    assert "title: 'TestOntology'" in retr_output
    assert "author: 'Author'" in retr_output
    assert "description: 'Test ontology'" in retr_output
    assert "type: 'Базовый'" in retr_output
    assert "date: '2024-01-01'" in retr_output

    assert 'types:' in retr_output
    assert "MyTypeParent: 'test label Term1', 'A test type1', { color: '#E6B8B7' }" in retr_output
    assert "MyTypeChild: 'test label Term2', 'A test type2'" in retr_output

    assert 'functions:' in retr_output
    assert ("MyFunction1: 'test label Func1' "
            "(MyTypeChild: 'test1 in1', MyTypeChild: 'test1 in2')"
            " -> MyTypeParent: 'test_type1', { colorArrow: '#E6B8B7' }") in retr_output

    assert 'hierarchy:' in retr_output
    assert 'MyTypeParent composition MyTypeChild'
