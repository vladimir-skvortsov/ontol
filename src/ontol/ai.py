import re
import warnings
from typing import Literal, Optional, Any

from pydantic import BaseModel, Field

from langchain_community.llms import Ollama
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.runnables.utils import Input
from langchain_core.output_parsers import PydanticOutputParser
from langchain.output_parsers import RetryOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableParallel

from ontol import (
    Ontology,
    Relationship,
    Function,
    RelationshipAttributes,
    RelationshipDirection,
    RelationshipType,
    Term,
)

warnings.filterwarnings('ignore')


class JsonExtractor(Runnable):
    json_pattern = r'\{.*\}'

    def invoke(
        self, input: Input, config: Optional[RunnableConfig] = None, **kwargs: Any
    ) -> str:
        matches = re.findall(JsonExtractor.json_pattern, input, re.DOTALL)

        if matches:
            return matches[-1].strip().replace('\\\\', '\\')

        return input


class RelationshipSchema(BaseModel):
    parent: str
    child: str
    relationship: Literal[
        'dependence',
        'association',
        'directAssociation',
        'inheritance',
        'implementation',
        'aggregation',
        'composition',
    ]
    label: Optional[str]
    is_bidirectional: bool
    comment: str


class HierarchyGenerationSchema(BaseModel):
    relationships: list[RelationshipSchema] = Field(
        description='Given the UML classes names, labels and functions where they are used, provide possible class diagram relationships. Also provide short comment why chose this relationship.'
    )


parser = PydanticOutputParser(pydantic_object=HierarchyGenerationSchema)

template = """
### Instructions

As a highly skilled UML expert, your task is to thoroughly analyze the classes and any associated functions provided.
Using this information, you will determine all possible relationships in a class diagram. Adhere to the following requirements:

1. Include relationships that define:
   - Parent class
   - Child class
   - Relationship type (e.g., inheritance, composition, aggregation, association, dependency)
   - Possible arrow label in UML style.
   - Additional comments, if necessary
   - Whether the relationship is bidirectional (true or false)
2. There can be no bidirectional inheritance relationships.
3. Derive as many relevant relationships as possible by examining the functions (methods) where these classes may be used.
4. Output only a JSON object following the format below (with each relationship as an item in a JSON array). Do not include any additional text or explanation beyond the JSON object.

### Context

Classes (name, label, and description, comma separated; may be empty):
```
{classes}
```

Functions (name, label, input arguments, and output argument with descriptions; may be empty):
```
{functions}
```

Format Instructions:
```
{format_instructions}
```

Your final output should be a JSON object listing all identified relationships. Return only this JSON object and nothing else.
"""

prompt = PromptTemplate(
    template=template,
    input_variables=['classes', 'functions'],
    partial_variables={'format_instructions': parser.get_format_instructions()},
)


class AI:
    def _format_string(self, string: str) -> str:
        return string.replace('\\n', '').strip().lower()

    def _format_terms(self, ontology: Ontology) -> str:
        return '\n'.join(
            [
                f"'{self._format_string(t.name)}', '{self._format_string(t.label)}', '{self._format_string(t.description)}'"
                for t in ontology.types
            ]
        )

    def _format_function(self, function: Function) -> str:
        function_line = f"'{self._format_string(function.name)}', '{self._format_string(function.label)}', ("
        args = ''
        for i, arg in enumerate(function.input_types):
            args += f"'{self._format_string(arg.term.name)}': '{self._format_string(arg.label)}'"
            if i < len(function.input_types) - 1:
                args += ', '
        function_line += (
            f'{args}) -> '
            f"'{self._format_string(function.output_type.term.name)}': '{self._format_string(function.output_type.label)}'"
        )

        return function_line

    def _format_functions(self, ontology: Ontology) -> str:
        return '\n'.join([self._format_function(f) for f in ontology.functions])

    def does_edge_exist(
        self, hierarchy: list[Relationship], relationship: Relationship
    ):
        for rel in hierarchy:
            if (
                rel.parent == relationship.parent
                and rel.children[0] == relationship.children[0]
            ):
                return True
        return False

    def generate_hierarchy(
        self, ontology: Ontology, model: str, temperature: float = 0.0
    ) -> tuple[list[Relationship], list[str]]:
        llm = Ollama(model=model, temperature=temperature)
        chain = prompt | llm | JsonExtractor() | parser

        relationships: list[Relationship] = []
        comments: list[str] = []
        formatted_terms = self._format_terms(ontology)
        formatted_functions = self._format_functions(ontology)

        try:
            response = chain.invoke(
                {'classes': formatted_terms, 'functions': formatted_functions}
            )

            for relationship in response.relationships:
                if relationship.relationship == 'inheritance':
                    relationship.parent, relationship.child = (
                        relationship.child,
                        relationship.parent,
                    )

                parent: Optional[Term] = ontology.find_term_by_name(relationship.parent)
                if parent is None:
                    continue

                relationship_type: Optional[RelationshipType] = (
                    RelationshipType.from_str(relationship.relationship)
                )
                if relationship_type is None:
                    continue

                child: Optional[Term] = ontology.find_term_by_name(relationship.child)
                if child is None:
                    continue

                children: list[Term] = [child]

                attributes: RelationshipAttributes = RelationshipAttributes(
                    title=relationship.label
                )
                if relationship.is_bidirectional:
                    attributes.direction = RelationshipDirection.BIDIRECTIONAL

                rel = Relationship(
                    parent=parent,
                    relationship=relationship_type,
                    children=children,
                    attributes=attributes,
                )

                if self.does_edge_exist(ontology.hierarchy + relationships, rel):
                    continue

                relationships.append(rel)
                comments.append(relationship.comment)
        except Exception as e:
            print(e)

        return relationships, comments
