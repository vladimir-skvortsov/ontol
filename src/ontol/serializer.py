import json
from typing import Any

from dataclasses import asdict

from ontol import Ontology, Term, Function, Meta, Relationship, Figure


class JSONSerializer:
    @staticmethod
    def serialize(ontology: Ontology) -> str:
        data: dict[str, object] = {
            'meta': JSONSerializer._serialize_meta(ontology.meta),
            'terms': [JSONSerializer._serialize_term(t) for t in ontology.types],
            'functions': [
                JSONSerializer._serialize_function(f) for f in ontology.functions
            ],
            'hierarchy': [
                JSONSerializer._serialize_relationship(r) for r in ontology.hierarchy
            ],
            'figures': [JSONSerializer._serialize_figure(f) for f in ontology.figures],
        }
        return json.dumps(data, ensure_ascii=False, indent=4)

    @staticmethod
    def _serialize_term(type_def: Term) -> dict[str, Any]:
        return {
            'name': type_def.name,
            'label': type_def.label,
            'description': type_def.description,
            'attributes': {
                key: value
                for key, value in asdict(type_def.attributes).items()
                if value is not None
            },
        }

    @staticmethod
    def _serialize_function(
        func_def: Function,
    ) -> dict[str, Any]:
        attributes = {
            key: value
            for key, value in asdict(func_def.attributes).items()
            if value is not None
        }

        if 'type' in attributes:
            attributes['type'] = attributes['type'].value

        return {
            'name': func_def.name,
            'label': func_def.label,
            'input_types': [
                {'name': t.term.name, 'label': t.label} for t in func_def.input_types
            ],
            'output_type': {
                'name': func_def.output_type.term.name,
                'label': func_def.output_type.label,
            },
            'attributes': attributes,
        }

    @staticmethod
    def _serialize_meta(meta: Meta) -> dict[str, str | None]:
        return asdict(meta)

    @staticmethod
    def _serialize_relationship(
        rel_def: Relationship,
    ) -> dict[str, Any]:
        attributes = {
            key: value
            for key, value in asdict(rel_def.attributes).items()
            if value is not None
        }

        if 'direction' in attributes:
            attributes['direction'] = attributes['direction'].value

        return {
            'name': rel_def.name,
            'parent': rel_def.parent.name,
            'relationship': rel_def.relationship.value,
            'children': [child.name for child in rel_def.children],
            'attributes': attributes,
        }

    @staticmethod
    def _serialize_figure(
        figure: Figure,
    ) -> dict[str, Any]:
        return {
            'name': figure.name,
            'terms': [term.name for term in figure.types],
            'functions': [func.name for func in figure.functions],
            'hierarchy': [rel.name for rel in figure.hierarchy],
        }
