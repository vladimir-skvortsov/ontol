from src.ontol import Function, Meta, Ontology, Relationship, Term


def test_term_creation() -> None:
    term: Term = Term(name='test_term', label='TestTerm', description='A test term')
    assert term.name == 'test_term'
    assert term.label == 'TestTerm'
    assert term.description == 'A test term'
    assert (
        repr(term)
        == 'Term(name=test_term, label=TestTerm, description=A test term, attributes={})'
    )


def test_term_with_attributes_creation() -> None:
    attributes = {'color': 'red'}
    term_with_attributes: Term = Term(
        name='test_term',
        label='TestTerm',
        description='A test term',
        attributes=attributes,
    )
    assert term_with_attributes.attributes == attributes
    assert (
        repr(term_with_attributes)
        == f'Term(name=test_term, label=TestTerm, description=A test term, attributes={attributes})'
    )


def test_term_with_empty_label_creation() -> None:
    term: Term = Term(name='test_term', label='', description='A test term')
    assert term.label == ''
    assert (
        repr(term)
        == 'Term(name=test_term, label=, description=A test term, attributes={})'
    )


def test_term_with_empty_description_creation() -> None:
    term: Term = Term(name='test_term', label='TestTerm', description='')
    assert term.description == ''
    assert (
        repr(term)
        == 'Term(name=test_term, label=TestTerm, description=, attributes={})'
    )


def test_function_creation():
    func: Function = Function(
        name='sum',
        label='Sum',
        input_types=[('int', 'First number'), ('int', 'Second number')],
        output_type=('int', 'Result'),
    )
    assert func.name == 'sum'
    assert func.label == 'Sum'
    assert func.input_types == [('int', 'First number'), ('int', 'Second number')]
    assert func.output_type == ('int', 'Result')
    assert (
        repr(func)
        == "Function(name=sum, label=Sum, input_types=[('int', 'First number'), ('int', 'Second number')], output_type=('int', 'Result'), attributes={})"
    )


def test_function_wth_empty_label_creation():
    func: Function = Function(
        name='sum',
        label='',
        input_types=[('int', 'First number'), ('int', 'Second number')],
        output_type=('int', 'Result'),
    )
    assert func.label == ''
    assert (
        repr(func)
        == "Function(name=sum, label=, input_types=[('int', 'First number'), ('int', 'Second number')], output_type=('int', 'Result'), attributes={})"
    )


def test_function_wth_empty_input_types_creation():
    func: Function = Function(
        name='sum',
        label='Sum',
        input_types=[],
        output_type=('int', 'Result'),
    )
    assert func.input_types == []
    assert (
        repr(func)
        == "Function(name=sum, label=Sum, input_types=[], output_type=('int', 'Result'), attributes={})"
    )


def test_relationship_creation() -> None:
    rel: Relationship = Relationship(
        parent='set', relationship='composite', child=['element']
    )
    assert rel.parent == 'set'
    assert rel.relationship == 'composite'
    assert rel.child == ['element']
    assert (
        repr(rel)
        == "Relationship(parent=set, relationship=composite, child=['element'], attributes={})"
    )


def test_meta_creation():
    meta: Meta = Meta(
        version='1.0',
        name='TestOntology',
        author='Author',
        description='A test ontology',
        type='Base',
        date_created='2024-01-01',
    )
    assert meta.version == '1.0'
    assert meta.name == 'TestOntology'
    assert meta.author == 'Author'
    assert meta.description == 'A test ontology'
    assert meta.type == 'Base'
    assert meta.date_created == '2024-01-01'
    assert (
        repr(meta)
        == 'Meta(version=1.0, name=TestOntology, author=Author, description=A test ontology, type=Base, date_created=2024-01-01)'
    )


def test_meta_with_empty_description_creation():
    meta_no_optional: Meta = Meta(
        version='1.0',
        name='TestOntology',
        author='Author',
        description=None,
        type='Base',
        date_created='2024-01-01',
    )
    assert meta_no_optional.description is None
    assert (
        repr(meta_no_optional)
        == 'Meta(version=1.0, name=TestOntology, author=Author, description=None, type=Base, date_created=2024-01-01)'
    )


def test_ontology_operations():
    ontology: Ontology = Ontology()
    char: Term = Term(name='str', label='String', description='')
    string: Term = Term(name='string', label='String', description='')
    concatanate: Function = Function(
        name='concatanate',
        label='Concatanate',
        input_types=[('str', ''), ('str', '')],
        output_type=('str', 'Result'),
    )
    rel: Relationship = Relationship(
        parent='string', relationship='composition', child='char'
    )
    meta: Meta = Meta(
        version='1.0',
        name='StringOntology',
        author='Author',
        description='A string ontology',
        date_created='2024-01-01',
    )

    ontology.add_type(char)
    ontology.add_type(string)
    ontology.add_function(concatanate)
    ontology.add_relationship(rel)
    ontology.set_meta(meta)

    assert ontology.types == [char, string]
    assert ontology.functions == [concatanate]
    assert ontology.hierarchy == [rel]
    assert ontology.meta == meta

    assert repr([char, string]) in repr(ontology)
    assert repr([concatanate]) in repr(ontology)
    assert repr([rel]) in repr(ontology)
    assert repr(meta) in repr(ontology)
