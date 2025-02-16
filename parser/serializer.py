import json
from parser.oast import Ontology, Term, Function, Meta


class JSONSerializer:
    def serialize(self, ontology: Ontology) -> str:
        data = {
            "terms": [self._serialize_term(t) for t in ontology.types],
            "functions": [self._serialize_function(f) for f in ontology.functions],
            "hierarchy": [expr.expression for expr in ontology.hierarchy],
            "meta": self._serialize_meta(ontology.meta) if ontology.meta else None,
        }
        return json.dumps(data, ensure_ascii=False, indent=4)

    def _serialize_term(self, type_def: Term) -> dict:
        return {"name": type_def.name, "description": type_def.description}

    def _serialize_function(self, func_def: Function) -> dict:
        return {
            "name": func_def.name,
            "input_types": func_def.input_types,
            "output_types": func_def.output_types,
            "label": func_def.label,
            "description": func_def.description,
        }

    def _serialize_meta(self, meta: Meta) -> dict:
        return {
            "version": meta.version,
            "name": meta.name,
            "author": meta.author,
            "description": meta.description,
            "date_created": meta.date_created,
        }
