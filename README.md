# Ontol DSL Parser

[![Build Status](https://github.com/vladimir-skvortsov/ontol/actions/workflows/check-tests.yaml/badge.svg)](https://github.com/vladimir-skvortsov/ontol/actions)
[![PyPi downloads](https://img.shields.io/pypi/dm/ontol.svg?label=Pypi%20downloads)](https://pypi.org/project/ontol)

**Authors:**
[Skvortsov Vladimir](https://github.com/vladimir-skvortsov),
[Aptukov Mikhail](https://github.com/LuckyAm20),
[Markov Mikhail](https://github.com/eagerbeaver04),
[Khamidullin Ilsaf](https://github.com/Ilsaffff),
[Afanasyev Andrew](https://github.com/afafos).

Ontol DSL Parser is a command-line tool for parsing and visualizing ontology files written in the Ontol DSL. It generates JSON representations and PlantUML diagrams from `.ontol` files.

## Features

-  Parse `.ontol` files to extract ontology structures.
-  Serialize ontology to JSON format.
-  Generate PlantUML diagrams from ontology.
-  Automatically render PlantUML diagrams to PNG images.
-  Watch files for changes and re-parse them automatically.
-  Display version and help information.

## Requirements

-  Python 3.9 or higher
-  Java (for local PlantUML rendering)
-  PlantUML (for local rendering)

## Installation

Install from PyPi:

```bash
pip install ontol
```

## Usage

### Parse a file

To parse an `.ontol` file and generate JSON and PlantUML files:

```bash
ontol path/to/yourfile.ontol
```

### Watch Mode

To watch a file for changes and automatically re-parse it:

```bash
ontol path/to/yourfile.ontol --watch
```

### Display Version

To display the version of the program:

```bash
ontol --version
```

### Help

To display help information:

```bash
ontol --help
```

### Tests

To display run tests:

```bash
pytest tests
```

## Output

- **JSON File**: A JSON representation of the ontology is saved with the same basename as the `.ontol` file.
- **PlantUML File**: A `.puml` file is generated for visualization.
- **PNG Image**: A PNG image is rendered from the PlantUML file.
