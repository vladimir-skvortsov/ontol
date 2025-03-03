from ontol import (
    Function,
    Meta,
    Ontology,
    Relationship,
    Term,
    FunctionArgument,
    PlantUML,
    RelationshipType,
    TermAttributes,
    FunctionAttributes,
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
    # TODO: add term without color attribute
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
    ontology.add_function(
        Function(
            name='MyFunction2',
            label='test label Func2',
            input_types=[FunctionArgument(Term('MyTypeChild'), 'test2 in1')],
            output_type=FunctionArgument(Term('MyTypeParent'), 'test_type2'),
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

    assert (
        '"test label Func1\\n(MyTypeChild: test1 in1, MyTypeChild: test1 in2 -> MyTypeParent: test_type1)"'
        ' as MyFunction1 #white' in uml_output
    )
    assert (
        '"test label Func2\\n(MyTypeChild: test2 in1 -> MyTypeParent: test_type2)" as MyFunction2 #white'
        in uml_output
    )
    print(uml_output)
    assert 'MyTypeChild "2" --[#E6B8B7]->  MyFunction1 ' in uml_output
    assert 'MyTypeChild  --[#black]->  MyFunction2 ' in uml_output
    assert 'MyFunction1  --[#E6B8B7]->  MyTypeParent ' in uml_output
    assert 'MyFunction2  --[#black]->  MyTypeParent ' in uml_output

    assert 'MyTypeParent  --[#black]-*  MyTypeChild ' in uml_output


def test_generate_type(generator: PlantUML):
    term = Term(name='MyType', description='A test type', label='test label')
    result = generator._generate_type(term)
    assert result == 'class MyType {\n  A test type\n}'


def test_generate_function(generator: PlantUML):
    func = Function(
        name='MyFunction',
        label='test label',
        input_types=[FunctionArgument(Term('int'), 'test')],
        output_type=FunctionArgument(Term('bool'), 'test'),
        attributes={'color': '#E6B8B7'},
    )
    result = generator._generate_function(func)
    assert 'MyFunction' in result
    assert 'class MyFunction <<Function>> {' in result
    assert '+MyFunction(int) : (bool)' in result
    assert 'test label' in result
    assert '}' in result


def test_generate_relationship(generator: PlantUML):
    relation = Relationship(
        parent=Term('MyTypeParent'),
        relationship=RelationshipType.from_str('aggregation'),
        children=[Term('MyTypeChild')],
    )
    result = generator._generate_relationship(relation)
    assert 'MyTypeParent' in result
    assert 'aggregation' in result
    assert 'MyTypeChild' in result
    assert 'as' in result
