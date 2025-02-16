import pytest
from parser.oast import Term, Function, Relationship, Meta, Ontology


def test_term_creation():
    term = Term(name="TestTerm", description="A test term")
    assert term.name == "TestTerm"
    assert term.description == "A test term"
    assert repr(term) == "Term(name=TestTerm, description=A test term)"

    term_no_desc = Term(name="NoDescTerm")
    assert term_no_desc.description is None
    assert repr(term_no_desc) == "Term(name=NoDescTerm, description=None)"


def test_function_creation():
    func = Function(
        name="TestFunction",
        input_types=["int", "str"],
        output_types=["bool"],
        description="A test function",
    )
    assert func.name == "TestFunction"
    assert func.input_types == ["int", "str"]
    assert func.output_types == ["bool"]
    assert func.description == "A test function"
    assert (
        repr(func)
        == "Function(name=TestFunction, input_types=['int', 'str'], output_types=['bool'], label=None, description=A test function)"
    )

    func_no_desc = Function(
        name="NoDescFunction", input_types=["float"], output_types=["str"]
    )
    assert func_no_desc.description is None
    assert (
        repr(func_no_desc)
        == "Function(name=NoDescFunction, input_types=['float'], output_types=['str'], label=None, description=None)"
    )

    func_with_label = Function(
        name="LabeledFunction",
        input_types=["int"],
        output_types=["str"],
        label="SomeLabel",
    )
    assert func_with_label.label == "SomeLabel"
    assert (
        repr(func_with_label)
        == "Function(name=LabeledFunction, input_types=['int'], output_types=['str'], label=SomeLabel, description=None)"
    )


def test_relationship_creation():
    rel = Relationship(expression="A > B")
    assert rel.expression == "A > B"
    assert repr(rel) == "Relationship(expression=A > B)"

    rel2 = Relationship(expression="C < D")
    assert rel2.expression == "C < D"
    assert repr(rel2) == "Relationship(expression=C < D)"


def test_meta_creation():
    meta = Meta(
        version="1.0",
        name="TestOntology",
        author="Author",
        description="A test ontology",
        date_created="2024-01-01",
    )
    assert meta.version == "1.0"
    assert meta.name == "TestOntology"
    assert meta.author == "Author"
    assert meta.description == "A test ontology"
    assert meta.date_created == "2024-01-01"
    assert (
        repr(meta)
        == "Meta(version=1.0, name=TestOntology, author=Author, description=A test ontology, date_created=2024-01-01)"
    )

    meta_no_optional = Meta(
        version="1.0",
        name="TestOntology",
        author="Author",
        description=None,
        date_created=None,
    )
    assert meta_no_optional.description is None
    assert meta_no_optional.date_created is None
    assert (
        repr(meta_no_optional)
        == "Meta(version=1.0, name=TestOntology, author=Author, description=None, date_created=None)"
    )


def test_ontology_operations():
    ontology = Ontology()
    term = Term(name="TestTerm")
    func = Function(name="TestFunction", input_types=["int"], output_types=["str"])
    rel = Relationship(expression="A > B")
    meta = Meta(
        version="1.0",
        name="TestOntology",
        author="Author",
        description="A test ontology",
        date_created="2024-01-01",
    )

    ontology.add_type(term)
    ontology.add_function(func)
    ontology.add_relationship(rel)
    ontology.set_meta(meta)

    assert ontology.types == [term]
    assert ontology.functions == [func]
    assert ontology.hierarchy == [rel]
    assert ontology.meta == meta

    with pytest.raises(
        ValueError, match="Meta information is already set and can only be set once."
    ):
        ontology.set_meta(meta)

    assert "Ontology(types=[Term(name=TestTerm, description=None)]" in repr(ontology)

    new_term = Term(name="NewTerm")
    new_func = Function(name="NewFunction", input_types=["str"], output_types=["int"])
    new_rel = Relationship(expression="B < A")

    ontology.add_type(new_term)
    ontology.add_function(new_func)
    ontology.add_relationship(new_rel)

    assert ontology.types == [term, new_term]
    assert ontology.functions == [func, new_func]
    assert ontology.hierarchy == [rel, new_rel]

    repr_str = repr(ontology)
    assert (
        "Ontology(types=[Term(name=TestTerm, description=None), Term(name=NewTerm, description=None)]"
        in repr_str
    )
    assert (
        "functions=[Function(name=TestFunction, input_types=['int'], output_types=['str'], label=None, description=None), Function(name=NewFunction, input_types=['str'], output_types=['int'], label=None, description=None)]"
        in repr_str
    )
