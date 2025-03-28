import os
import re
import time
from typing import Optional, List
import glob

from unidecode import unidecode

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from watchdog.observers.api import BaseObserver

from argparse import ArgumentParser, Namespace

from ontol import (
    Parser,
    JSONSerializer,
    PlantUML,
    Retranslator,
    Ontology,
    Figure,
    AI,
    constants,
)

__VERSION__ = os.getenv('ONTOL_VERSION', 'dev')


class CLI:
    def __init__(self) -> None:
        self.args_parser: ArgumentParser = ArgumentParser(
            description='Ontol DSL Parser - A tool for parsing and visualizing ontology files written in the Ontol DSL.'
        )
        self.args_parser.add_argument(
            'file',
            type=str,
            help='Path to the .ontol file to be parsed. Supports wildcards and directories.',
        )
        self.args_parser.add_argument(
            '-w',
            '--watch',
            action='store_true',
            default=False,
            help='Watch the specified file(s) for changes and re-parse automatically',
        )
        self.args_parser.add_argument(
            '-d',
            '--debug',
            action='store_true',
            default=False,
            help='Get retranslation version of the file .ontol',
        )
        self.args_parser.add_argument(
            '-q',
            '--quiet',
            action='store_true',
            default=False,
            help='Ignore all the warnings',
        )
        self.args_parser.add_argument(
            '--output-dir',
            dest='output_dir',
            type=str,
            help='Output directory to write files in',
        )
        self.args_parser.add_argument(
            '--gen-hierarchy',
            dest='gen_hierarchy',
            action='store_true',
            default=False,
            help='Generate additional hierarchy relationship using Ollama model',
        )
        self.args_parser.add_argument(
            '-m',
            '--model',
            type=str,
            default='llama3.1',
            help='Ollama model to use',
        )
        self.args_parser.add_argument(
            '-t',
            '--temperature',
            type=float,
            default=0.0,
            help='Model temperature to use',
        )
        self.args_parser.add_argument(
            '--split-funcs-rels',
            dest='split_funcs_rels',
            action='store_true',
            default=False,
            help='Split functions and relations',
        )
        self.args_parser.add_argument(
            '-v',
            '--version',
            action='version',
            version=f'%(prog)s {__VERSION__}',
            help='Show the version of the program and exit',
        )
        self.args_parser.add_argument(
            '--max-edges',
            dest='max_edges',
            type=int,
            help='Set max edges in scheme',
        )

        self.parser: Parser = Parser()
        self.serializer: JSONSerializer = JSONSerializer()
        self.plantuml: PlantUML = PlantUML()
        self.retranslator: Retranslator = Retranslator()
        self.ai: AI = AI()

    def run(self) -> None:
        args: Namespace = self.args_parser.parse_args()

        file_paths = self.get_file_paths(args.file)
        # Ensure we attempt to parse even non-existent files
        if not file_paths:
            file_paths = [args.file]

        if args.watch:
            for file_path in file_paths:
                self.watch_file(file_path, args)
        else:
            for file_path in file_paths:
                self.parse_file(file_path, args)

    def get_file_paths(self, path: str) -> List[str]:
        # Check if the path is a directory
        if os.path.isdir(path):
            # Recursively find all .ontol files
            ontol_files = []
            for root, _, files in os.walk(path):
                for file in files:
                    if file.endswith('.ontol'):
                        ontol_files.append(os.path.join(root, file))
            return ontol_files
        # If not a directory, assume it's a pattern or a file
        else:
            return glob.glob(path, recursive=True)

    def parse_file(self, file_path: str, args: Optional[Namespace] = None) -> None:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content: str = file.read()
                ontology, warnings = self.parser.parse(content, file_path)

                if (
                    args
                    and args.max_edges
                    and (count := ontology.count_edges()) > args.max_edges
                ):
                    warnings.append(
                        f'{constants.warning_prefix} too much edges. Expected: '
                        f'{args.max_edges}, got: {count}'
                    )

                # Print warnings
                if warnings and (not args or not args.quiet):
                    print('\n\n'.join(warnings))

                if args and args.gen_hierarchy:
                    print('Generating hierarchy...')
                    hierarchy, comments = self.ai.generate_hierarchy(
                        ontology, args.model, args.temperature
                    )
                    ontology.hierarchy.extend(hierarchy)
                    print('\nGenerated relationships:')
                    for relationship, comment in zip(hierarchy, comments):
                        print(
                            f'{relationship.parent.name} {relationship.relationship.value} {relationship.children[0].name}: {comment}'
                        )

                base_dir = os.path.dirname(file_path)
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                output_dir = args.output_dir if args and args.output_dir else base_dir

                if output_dir:
                    os.makedirs(output_dir, exist_ok=True)

                ontologies: list[Ontology] = [ontology]
                base_names: list[str] = [base_name]

                for figure in ontology.figures:
                    ontologies.append(Ontology.from_figure(ontology, figure))
                    file_postfix = self.get_figure_file_postfix(figure)
                    base_names.append(f'{base_name}_{file_postfix}')

                if args and args.split_funcs_rels:
                    new_ontologies: list[Ontology] = []
                    new_base_names: list[str] = []

                    for ontology, base_name in zip(ontologies, base_names):
                        new_ontologies.extend(
                            [ontology.without_functions, ontology.only_functions]
                        )
                        new_base_names.extend(
                            [f'{base_name}_rels', f'{base_name}_funcs']
                        )

                    ontologies.extend(new_ontologies)
                    base_names.extend(new_base_names)

                for ontology, base_name in zip(ontologies, base_names):
                    # JSON
                    json_content: str = self.serializer.serialize(ontology)
                    json_file_path: str = os.path.join(output_dir, f'{base_name}.json')
                    with open(json_file_path, 'w', encoding='utf-8') as json_file:
                        json_file.write(json_content)

                    # PlantUML
                    plantuml_content: str = self.plantuml.generate(ontology)
                    puml_file_path: str = os.path.join(output_dir, f'{base_name}.puml')
                    with open(puml_file_path, 'w', encoding='utf-8') as puml_file:
                        puml_file.write(plantuml_content)
                    self.plantuml.processes_puml_to_png(puml_file_path)

                    # Retranslator
                    if args and not args.debug:
                        continue
                    retranslator_content: str = self.retranslator.translate(ontology)
                    retranslator_file_path: str = os.path.join(
                        output_dir, f'{base_name}_retr.ontol'
                    )
                    with open(
                        retranslator_file_path, 'w', encoding='utf-8'
                    ) as retr_file:
                        retr_file.write(retranslator_content)
        except FileNotFoundError:
            print(f"{constants.error_prefix} the file '{file_path}' does not exist.")
        except Exception as e:
            print(f'{constants.error_prefix} error processing file {file_path}: {e}')

    def watch_file(self, file_path: str, args: Optional[Namespace] = None):
        self.parse_file(file_path, args)

        class FileChangeHandler(FileSystemEventHandler):
            def __init__(self, parse_callback):
                super().__init__()
                self.parse_callback = parse_callback

            def on_modified(self, event):
                if event.src_path.endswith('.ontol'):
                    print(f'File {event.src_path} modified, re-parsing...')
                    self.parse_callback(event.src_path, args)

        event_handler: FileChangeHandler = FileChangeHandler(self.parse_file)

        observer: BaseObserver = Observer()
        observer.schedule(event_handler, path=file_path, recursive=True)
        observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

    def get_figure_file_postfix(self, figure: Figure) -> str:
        file_postfix: str = figure.name.strip().lower()
        file_postfix = unidecode(file_postfix)
        file_postfix = re.sub(r'[^a-zA-Z0-9\s]', ' ', file_postfix)
        file_postfix = re.sub(r'\s+', ' ', file_postfix)
        file_postfix = re.sub(r'\s', '_', file_postfix)
        return file_postfix


def main():
    cli: CLI = CLI()
    cli.run()


if __name__ == '__main__':
    main()
