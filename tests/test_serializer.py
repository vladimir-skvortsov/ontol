import json

from ontol.oast import TypeDict, RelationshipType
from src.ontol import Function, Meta, Ontology, Relationship, Term, JSONSerializer

import pytest


@pytest.fixture
def sample_ontology():
    ontology = Ontology()
    ontology.add_type(
        Term(name='MyType', description='A sample type', label='A some label')
    )
    input_type: TypeDict = {'name': Term('int'), 'label': ''}
    ontology.add_function(
        Function(
            name='MyFunction',
            label='Function',
            input_types=[input_type],
            output_type={'name': Term('bool'), 'label': ''},
        )
    )
    ontology.add_relationship(
        Relationship(
            relationship=RelationshipType.DEPENDS,
            parent=Term('int'),
            children=[Term('bool')],
        )
    )
    ontology.set_meta(
        Meta(
            version='1.0',
            title='SampleOntology',
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
    assert data['terms'] == [
        {
            'name': 'MyType',
            'label': 'A some label',
            'description': 'A sample type',
            'attributes': {},
        }
    ]
    assert data['functions'] == [
        {
            'name': 'MyFunction',
            'label': 'Function',
            'input_types': [
                {
                    'name': {
                        'name': 'int',
                        'label': '',
                        'description': '',
                        'attributes': {},
                    },
                    'label': '',
                }
            ],
            'output_type': {
                'name': {
                    'name': 'bool',
                    'label': '',
                    'description': '',
                    'attributes': {},
                },
                'label': '',
            },
            'attributes': {},
        }
    ]

    assert data['hierarchy'] == [
        {
            'parent': {'name': 'int', 'label': '', 'description': '', 'attributes': {}},
            'relationship': 'depends',
            'children': [
                {'name': 'bool', 'label': '', 'description': '', 'attributes': {}}
            ],
            'attributes': {},
        }
    ]
    assert data['meta'] == {
        'version': '1.0',
        'title': 'SampleOntology',
        'author': 'Author',
        'description': 'Sample description',
        'type': 'Базовый',
        'date_created': '2024-01-01',
    }


def test_serialize_empty_ontology(serializer):
    ontology = Ontology()
    json_output = serializer.serialize(ontology)
    data = json.loads(json_output)
    assert data == {
        'terms': [],
        'functions': [],
        'hierarchy': [],
        'meta': {
            'version': None,
            'title': None,
            'author': None,
            'description': None,
            'type': None,
            'date_created': None,
        },
    }


def test_serialize_term(serializer):
    term = Term(name='TestTerm', description='A test term', label='A test label')
    serialized_term = serializer._serialize_term(term)
    assert serialized_term == {
        'name': 'TestTerm',
        'label': 'A test label',
        'description': 'A test term',
        'attributes': {},
    }


def test_serialize_function(serializer):
    func = Function(
        name='TestFunction',
        input_types=[{'name': Term('int'), 'label': ''}],
        output_type={'name': Term('bool'), 'label': ''},
        label='A test function',
    )
    serialized_function = serializer._serialize_function(func)
    print(serialized_function)
    assert serialized_function == {
        'name': 'TestFunction',
        'label': 'A test function',
        'input_types': [
            {
                'name': {
                    'name': 'int',
                    'label': '',
                    'description': '',
                    'attributes': {},
                },
                'label': '',
            }
        ],
        'output_type': {
            'name': {'name': 'bool', 'label': '', 'description': '', 'attributes': {}},
            'label': '',
        },
        'attributes': {},
    }


def test_serialize_meta(serializer):
    meta = Meta(
        version='1.0',
        title='TestOntology',
        author='Author',
        description='A test ontology',
        type='Базовый',
        date_created='2024-01-01',
    )
    serialized_meta = serializer._serialize_meta(meta)
    assert serialized_meta == {
        'version': '1.0',
        'title': 'TestOntology',
        'author': 'Author',
        'description': 'A test ontology',
        'type': 'Базовый',
        'date_created': '2024-01-01',
    }


def test_serialize_ontology_without_meta(serializer):
    ontology = Ontology()
    ontology.add_type(
        Term(name='MyType', description='A sample type', label='A some label')
    )
    ontology.add_function(
        Function(
            name='MyFunction',
            label='Function',
            input_types=[{'name': Term('int'), 'label': ''}],
            output_type={'name': Term('bool'), 'label': ''},
        )
    )
    ontology.add_relationship(
        Relationship(
            relationship=RelationshipType.DEPENDS,
            parent=Term('int'),
            children=[Term('bool')],
        )
    )

    json_output = serializer.serialize(ontology)
    data = json.loads(json_output)

    assert 'terms' in data
    assert 'functions' in data
    assert 'hierarchy' in data
    assert data['meta'] == {
        'version': None,
        'title': None,
        'author': None,
        'description': None,
        'type': None,
        'date_created': None,
    }
    assert data['terms'] == [
        {
            'name': 'MyType',
            'label': 'A some label',
            'description': 'A sample type',
            'attributes': {},
        }
    ]
    assert data['functions'] == [
        {
            'name': 'MyFunction',
            'label': 'Function',
            'input_types': [
                {
                    'name': {
                        'name': 'int',
                        'label': '',
                        'description': '',
                        'attributes': {},
                    },
                    'label': '',
                }
            ],
            'output_type': {
                'name': {
                    'name': 'bool',
                    'label': '',
                    'description': '',
                    'attributes': {},
                },
                'label': '',
            },
            'attributes': {},
        }
    ]

    assert data['hierarchy'] == [
        {
            'parent': {'name': 'int', 'label': '', 'description': '', 'attributes': {}},
            'relationship': 'depends',
            'children': [
                {'name': 'bool', 'label': '', 'description': '', 'attributes': {}}
            ],
            'attributes': {},
        }
    ]
