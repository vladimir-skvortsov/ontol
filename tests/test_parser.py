import unittest
from parser import Parser

class TestParser(unittest.TestCase):
    def setUp(self):
        self.parser = Parser()

    def test_parse_type(self):
        content = "type set \"Множество - это коллекция уникальных элементов\""
        ontology = self.parser.parse(content)
        self.assertEqual(len(ontology.types), 1)
        self.assertEqual(ontology.types[0].name, "set")
        self.assertEqual(ontology.types[0].description, "Множество - это коллекция уникальных элементов")

    def test_parse_function(self):
        content = "function decart (set, set) -> (set) \"Декартово произведение\" \"Декартово произведение двух множеств\""
        ontology = self.parser.parse(content)
        self.assertEqual(len(ontology.functions), 1)
        func = ontology.functions[0]
        self.assertEqual(func.name, "decart")
        self.assertEqual(func.input_types, ["set", "set"])
        self.assertEqual(func.output_types, ["set"])
        self.assertEqual(func.label, "Декартово произведение")
        self.assertEqual(func.description, "Декартово произведение двух множеств")

    def test_parse_logical_expression(self):
        content = "element1 in set1 and element2 in set2"
        ontology = self.parser.parse(content)
        self.assertEqual(len(ontology.logical_expressions), 1)
        self.assertEqual(ontology.logical_expressions[0].expression, "element1 in set1 and element2 in set2")

    def test_parse_meta(self):
        content = "meta 1.0 \"Пример Онтологии\" \"Алексей Иванов\" \"Описание онтологии\""
        ontology = self.parser.parse(content)
        self.assertIsNotNone(ontology.meta)
        self.assertEqual(ontology.meta.version, "1.0")
        self.assertEqual(ontology.meta.name, "Пример Онтологии")
        self.assertEqual(ontology.meta.author, "Алексей Иванов")
        self.assertEqual(ontology.meta.description, "Описание онтологии")

    def test_parse_comments(self):
        content = "# Это комментарий\n# Еще один комментарий"
        ontology = self.parser.parse(content)
        self.assertEqual(len(ontology.comments), 2)
        self.assertEqual(ontology.comments[0].text, "Это комментарий")
        self.assertEqual(ontology.comments[1].text, "Еще один комментарий")

    def test_combined_parsing(self):
        content = """
        # Комментарий
        meta 1.0 "Пример Онтологии" "Алексей Иванов" "Описание онтологии"
        type set "Множество - это коллекция уникальных элементов"
        function decart (set, set) -> (set) "Декартово произведение" "Декартово произведение двух множеств"
        element1 in set1 and element2 in set2
        """
        ontology = self.parser.parse(content)
        self.assertEqual(len(ontology.comments), 1)
        self.assertEqual(len(ontology.types), 1)
        self.assertEqual(len(ontology.functions), 1)
        self.assertEqual(len(ontology.logical_expressions), 1)
        self.assertIsNotNone(ontology.meta)

if __name__ == '__main__':
    unittest.main()
