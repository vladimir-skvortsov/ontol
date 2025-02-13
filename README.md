# Ontol DSL Parser

**Authors:**
[Skvortsov Vladimir](https://github.com/vladimir-skvortsov),
[Aptukov Mikhail](https://github.com/LuckyAm20),
[Markov Mikhail](https://github.com/eagerbeaver04),
[Afanasyev Andrew](https://github.com/afafos),
[Khamidullin Ilsaf](https://github.com/Ilsaffff)

Ontol DSL Parser - A tool for parsing and visualizing ontology files written in the Ontol DSL.

## Features

-  Parse `.ontol` files to extract ontology structures.
-  Serialize ontology to JSON format.
-  Generate PlantUML diagrams from ontology.
-  Automatically render PlantUML diagrams to PNG images.
-  Watch files for changes and re-parse them automatically.
-  Display version and help information.

## Usage

Get help:

```bash
python parser/cli.py --help
```

Parse a file:

```bash
python parser/cli.py examples/test.ontol
```

Watch a file:

```bash
python parser/cli.py examples/test.ontol --watch
```
