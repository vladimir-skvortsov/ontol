from parser.oast import Ontology, Term, Function, Relationship, Meta

class Parser:
  def __init__(self):
    pass

  def parse(self, file_content: str) -> Ontology:
    ontology = Ontology()

    lines = file_content.splitlines()

    for line in lines:
      line = line.strip()
      if line.startswith("#"):  # Это комментарий
        continue
      elif line.startswith("type"):
        type_def = self._parse_type(line)
        ontology.add_type(type_def)
      elif line.startswith("function"):
        func_def = self._parse_function(line)
        ontology.add_function(func_def)
      elif line.startswith("meta"):
        meta = self._parse_meta(line)
        ontology.set_meta(meta)
      elif line:
        logical_expr = Relationship(line)
        ontology.add_relationship(logical_expr)

    return ontology

  def _parse_type(self, line: str) -> Term:
    parts = line.split()
    name = parts[1]
    description = " ".join(parts[2:]) if len(parts) > 2 else None
    return Term(name, description)

  def _parse_function(self, line: str) -> Function:
    parts = line.split()
    name = parts[1]
    input_types = parts[2].strip("()").split(",")
    output_types = parts[3].strip("()").split(",")
    label = parts[4] if len(parts) > 4 else None
    description = " ".join(parts[5:]) if len(parts) > 5 else None
    return Function(name, input_types, output_types, label, description)

  def _parse_meta(self, line: str) -> Meta:
    parts = line.split()
    version = parts[1]
    name = parts[2]
    author = parts[3]
    description = " ".join(parts[4:]) if len(parts) > 4 else ""
    date_created = "2025-02-08"
    return Meta(version, name, author, description, date_created)
