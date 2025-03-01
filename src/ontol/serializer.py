import json

from dataclasses import asdict

from ontol import Ontology, Term, Function, Meta, Relationship


class JSONSerializer:
    @staticmethod
    def serialize(ontology: Ontology) -> str:
        data: dict[str, object] = {
            'terms': [JSONSerializer._serialize_term(t) for t in ontology.types],
            'functions': [
                JSONSerializer._serialize_function(f) for f in ontology.functions
            ],
            'hierarchy': [
                JSONSerializer._serialize_relationship(r) for r in ontology.hierarchy
            ],
            'meta': JSONSerializer._serialize_meta(ontology.meta)
            if ontology.meta
            else None,
        }
        return json.dumps(data, ensure_ascii=False, indent=4)

    @staticmethod
    def _serialize_term(type_def: Term) -> dict[str, str | None]:
        return asdict(type_def)

    @staticmethod
    def _serialize_function(
        func_def: Function,
    ) -> dict[str, str | list[dict] | dict | None]:
        return {
            'name': func_def.name,
            'label': func_def.label,
            'input_types': [
                {'name': asdict(t['name']), 'label': t['label']}
                for t in func_def.input_types
            ],
            'output_type': {
                'name': asdict(func_def.output_type['name']),
                'label': func_def.output_type['label'],
            },
            'attributes': func_def.attributes,
        }

    @staticmethod
    def _serialize_meta(meta: Meta) -> dict[str, str | None]:
        return asdict(meta)

    @staticmethod
    def _serialize_relationship(
        rel_def: Relationship,
    ) -> dict[str, str | list[str] | dict[str, str]]:
        return {
            'parent': asdict(rel_def.parent),
            'relationship': rel_def.relationship.value,
            'children': [asdict(child) for child in rel_def.children],
            'attributes': rel_def.attributes,
        }
