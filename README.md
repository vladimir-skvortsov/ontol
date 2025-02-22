# Ontol DSL Parser

**Authors:**
[Skvortsov Vladimir](https://github.com/vladimir-skvortsov),
[Aptukov Mikhail](https://github.com/LuckyAm20),
[Markov Mikhail](https://github.com/eagerbeaver04),
[Afanasyev Andrew](https://github.com/afafos),
[Khamidullin Ilsaf](https://github.com/Ilsaffff).

Ontol DSL Parser is a command-line tool for parsing and visualizing ontology files written in the Ontol DSL. It generates JSON representations and PlantUML diagrams from `.ontol` files.

## Features

-  Parse `.ontol` files to extract ontology structures.
-  Serialize ontology to JSON format.
-  Generate PlantUML diagrams from ontology.
-  Automatically render PlantUML diagrams to PNG images.
-  Watch files for changes and re-parse them automatically.
-  Display version and help information.

## Requirements

-  Python 3.7 or higher
-  Java (for local PlantUML rendering)
-  PlantUML (for local rendering)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/vladimir-skvortsov/ontol.git
cd ontol
```

2.	Install the required Python packages:

```bash
pip install -r requirements.txt
```

## Usage

### Parse a file

To parse an `.ontol` file and generate JSON and PlantUML files:

```bash
python -m src.cli path/to/yourfile.ontol
```

### Watch Mode

To watch a file for changes and automatically re-parse it:

```bash
python -m src.cli path/to/yourfile.ontol --watch
```

### Display Version

To display the version of the program:

```bash
python -m src.cli --version
```

### Help

To display help information:

```bash
python -m src.cli --help
```

### Test

To display test information:

```bash
pytest tests
```

## Output

- **JSON File**: A JSON representation of the ontology is saved with the same basename as the `.ontol` file.
- **PlantUML File**: A `.puml` file is generated for visualization.
- **PNG Image**: A PNG image is rendered from the PlantUML file.
