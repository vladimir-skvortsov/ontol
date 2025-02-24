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
    ontology.add_type(Term(name='MyTypeParent', label='test label Term1', description='A test type1',
                           attributes={'color': '#E6B8B7'}))
    ontology.add_type(Term(name='MyTypeChild', label='test label Term2', description='A test type2'))
    ontology.add_function(
        Function(
            name='MyFunction1',
            label='test label Func1',
            input_types=[('int', 'test1 in1'), ('str', 'test1 in2')],
            output_type=('bool', 'test_type1'),
            attributes={'colorArrow': '#E6B8B7'}
        )
    )
    ontology.add_function(
        Function(
            name='MyFunction2',
            label='test label Func2',
            input_types=[('str', 'test2 in1'), ('float', 'test2 in2')],
            output_type=('str', 'test_type2')
        )
    )
    ontology.add_relationship(
        Relationship(
            parent='MyTypeParent',
            relationship='composition',
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

    assert 'MyTypeParent' in uml_output
    assert 'test label Term1' in uml_output
    assert '(A test type1)' in uml_output
    assert '#E6B8B7' in uml_output
    assert 'MyTypeChild' in uml_output
    assert 'test label Term2' in uml_output
    assert '(A test type2)' in uml_output
    assert '#white' in uml_output

    assert ('"test label Func1\\n(int: test1 in1, str: test1 in2 -> bool: test_type1)" as MyFunction1 #white'
            in uml_output)
    assert ('"test label Func2\\n(str: test2 in1, float: test2 in2 -> str: test_type2)" as MyFunction2 #white'
            in uml_output)

    assert 'int "" --[#E6B8B7]-> "" MyFunction1 : ""' in uml_output
    assert 'str "" --[#E6B8B7]-> "" MyFunction1 : ""' in uml_output
    assert 'MyFunction1 "" --[#E6B8B7]-> "" bool : ""' in uml_output

    assert 'str "" --[#black]-> "" MyFunction2 : ""' in uml_output
    assert 'float "" --[#black]-> "" MyFunction2 : ""' in uml_output
    assert 'MyFunction2 "" --[#black]-> "" str : ""' in uml_output

    assert 'MyTypeParent "" --[#black]-* "" MyTypeChild : ""' in uml_output


def test_generate_type(generator: PlantUML):
    term = Term(name='MyType', description='A test type', label='test label')
    result = generator._generate_type(term)
    assert result == 'class MyType {\n  A test type\n}'


def test_generate_function(generator: PlantUML):
    func = Function(
        name='MyFunction',
        label='test label',
        input_types=[('int', 'test')],
        output_type=('bool', "test"),
        attributes={'color': '#E6B8B7'}
    )
    result = generator._generate_function(func)
    assert 'MyFunction' in result
    assert 'class MyFunction <<Function>> {' in result
    assert '+MyFunction(int) : (bool)' in result
    assert 'test label' in result
    assert '}' in result


def test_generate_logical_expression(generator: PlantUML):
    relation = Relationship(
        parent='MyTypeParent',
        relationship='containsAAAA',
        child=['MyTypeChild'],
    )
    result = generator._generate_relationship(relation)
    print(result)
    assert 'MyTypeParent' in result
    assert 'containsAAAA' in result
    assert 'MyTypeChild' in result
    assert 'as' in result