from src.parser import Parser

import pytest


@pytest.fixture
def parser():
    return Parser()


def test_parse_type(parser):
    content = 'type set "Множество - это коллекция уникальных элементов"'
    ontology = parser.parse(content)
    assert len(ontology.types) == 1
    assert ontology.types[0].name == 'set'
    assert (
        ontology.types[0].description
        == 'Множество - это коллекция уникальных элементов'
    )


def test_parse_function(parser):
    content = 'function decart (set,set) -> (set) "Декартово произведение" "Декартово произведение двух множеств"'
    ontology = parser.parse(content)
    assert len(ontology.functions) == 1
    func = ontology.functions[0]
    assert func.name == 'decart'
    assert func.input_types == ['set', 'set']
    assert func.output_types == ['set']
    assert func.label == 'Декартово произведение'
    assert func.description == 'Декартово произведение двух множеств'


def test_parse_heierarchy(parser):
    content = 'element1 in set1 and element2 in set2'
    ontology = parser.parse(content)
    assert len(ontology.hierarchy) == 1
    assert ontology.hierarchy[0].expression == 'element1 in set1 and element2 in set2'


def test_parse_meta(parser):
    content = 'meta 1.0 "Пример Онтологии" "Алексей Иванов" "Описание онтологии"'
    ontology = parser.parse(content)
    assert ontology.meta is not None
    assert ontology.meta.version == '1.0'
    assert ontology.meta.name == 'Пример Онтологии'
    assert ontology.meta.author == 'Алексей Иванов'
    assert ontology.meta.description == 'Описание онтологии'


def test_combined_parsing(parser):
    content = """
    # Комментарий
    meta 1.0 "Пример Онтологии" "Алексей Иванов" "Описание онтологии"
    type set "Множество - это коллекция уникальных элементов"
    function decart (set, set) -> (set) "Декартово произведение" "Декартово произведение двух множеств"
    element1 in set1 and element2 in set2
    """
    ontology = parser.parse(content)
    assert len(ontology.comments) == 1
    assert len(ontology.types) == 1
    assert len(ontology.functions) == 1
    assert len(ontology.logical_expressions) == 1
    assert ontology.meta is not None
