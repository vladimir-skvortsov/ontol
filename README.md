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

### Debug mode
To enable debug mode, which retranslates the output back to the .ontol file:

```bash
ontol path/to/yourfile.ontol --debug
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

## Debug mode 
When the `--debug` flag is used, the parser retranslates the output back to the .ontol file. This is particularly useful for debugging, as it allows you to verify the accuracy and consistency of the parsing process. The retranslated file is saved with the same name as the original .ontol file, enabling easy comparison between the original and retranslated versions.

## Contributing
Contributions are welcome! If you'd like to contribute, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes.
4. Ensure all tests pass by running `pytest tests`.
5. Submit a pull request.

## License 
This project is licensed under the Apache-2.0 License. See the LICENSE file for details.

## Acknowledgments
* Thanks to the [PlantUML team](https://github.com/plantuml) for providing an excellent tool for diagram generation.
* Special thanks to all contributors and users of the Ontol DSL Parser.
* A heartfelt thank you to [Danil Pestryakov](https://github.com/DanilPestryakov) and [Nikita Motorny](https://github.com/motorny) for their inspiration and support.
