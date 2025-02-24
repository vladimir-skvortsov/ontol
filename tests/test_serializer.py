import json
from src.ontol import Function, Meta, Ontology, Relationship, Term, JSONSerializer

import pytest


@pytest.fixture
def sample_ontology():
    ontology = Ontology()
    ontology.add_type(Term(name='MyType', description='A sample type'))
    ontology.add_function(
        Function(
            name='MyFunction',
            input_types=['int'],
            output_types=['bool'],
            description='A sample function',
        )
    )
    ontology.add_relationship(Relationship(expression='A > B'))
    ontology.set_meta(
        Meta(
            version='1.0',
            name='SampleOntology',
            author='Author',
            description='Sample description',
            type='Базовый',
            date_created='2024-01-01',
        )
    )
    return ontology


@pytest.fixture
def serializer():
    return JSONSerializer()


def test_serialize_ontology(serializer, sample_ontology):
    json_output = serializer.serialize(sample_ontology)
    data = json.loads(json_output)

    assert 'terms' in data
    assert 'functions' in data
    assert 'hierarchy' in data
    assert 'meta' in data

    assert data['terms'] == [{'name': 'MyType', 'description': 'A sample type'}]
    assert data['functions'] == [
        {
            'name': 'MyFunction',
            'input_types': ['int'],
            'output_types': ['bool'],
            'label': None,
            'description': 'A sample function',
        }
    ]
    assert data['hierarchy'] == ['A > B']
    assert data['meta'] == {
        'version': '1.0',
        'name': 'SampleOntology',
        'author': 'Author',
        'description': 'Sample description',
        'type': 'Базовый',
        'date_created': '2024-01-01',
    }


def test_serialize_empty_ontology(serializer):
    ontology = Ontology()
    json_output = serializer.serialize(ontology)
    data = json.loads(json_output)

    assert data == {'terms': [], 'functions': [], 'hierarchy': [], 'meta': None}


def test_serialize_term(serializer):
    term = Term(name='TestTerm', description='A test term')
    serialized_term = serializer._serialize_term(term)
    assert serialized_term == {'name': 'TestTerm', 'description': 'A test term'}


def test_serialize_function(serializer):
    func = Function(
        name='TestFunction',
        input_types=['int'],
        output_types=['str'],
        description='A test function',
    )
    serialized_function = serializer._serialize_function(func)
    assert serialized_function == {
        'name': 'TestFunction',
        'input_types': ['int'],
        'output_types': ['str'],
        'label': None,
        'description': 'A test function',
    }


def test_serialize_meta(serializer):
    meta = Meta(
        version='1.0',
        name='TestOntology',
        author='Author',
        description='A test ontology',
        type='Базовый',
        date_created='2024-01-01',
    )
    serialized_meta = serializer._serialize_meta(meta)
    assert serialized_meta == {
        'version': '1.0',
        'name': 'TestOntology',
        'author': 'Author',
        'description': 'A test ontology',
        'type': 'Базовый',
        'date_created': '2024-01-01',
    }


def test_serialize_ontology_without_meta(serializer):
    ontology = Ontology()
    ontology.add_type(Term(name='MyType'))
    ontology.add_function(
        Function(name='MyFunction', input_types=['int'], output_types=['bool'])
    )
    ontology.add_relationship(Relationship(expression='A > B'))

    json_output = serializer.serialize(ontology)
    data = json.loads(json_output)

    assert 'terms' in data
    assert 'functions' in data
    assert 'hierarchy' in data
    assert data['meta'] is None  # Meta should be None

    assert data['terms'] == [{'name': 'MyType', 'description': None}]
    assert data['functions'] == [
        {
            'name': 'MyFunction',
            'input_types': ['int'],
            'output_types': ['bool'],
            'label': None,
            'description': None,
        }
    ]
    assert data['hierarchy'] == ['A > B']
