import os
import time
from typing import Optional

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
    AI,
)


__VERSION__ = os.getenv('ONTOL_VERSION', 'dev')


class CLI:
    def __init__(self) -> None:
        self.args_parser: ArgumentParser = ArgumentParser(
            description='Ontol DSL Parser - A tool for parsing and visualizing ontology files written in the Ontol DSL.'
        )
        self.args_parser.add_argument(
            'file', type=str, help='Path to the .ontol file to be parsed'
        )
        self.args_parser.add_argument(
            '-w',
            '--watch',
            action='store_true',
            default=False,
            help='Watch the specified file for changes and re-parse automatically',
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
            '--dir',
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
            '--model',
            type=str,
            default='llama3.1',
            help='Ollama model to use',
        )
        self.args_parser.add_argument(
            '--temperature',
            type=float,
            default=0.0,
            help='Model temperature to use',
        )
        self.args_parser.add_argument(
            '-v',
            '--version',
            action='version',
            version=f'%(prog)s {__VERSION__}',
            help='Show the version of the program and exit',
        )

        self.watch: bool = False
        self.debug: bool = False
        self.quiet: bool = False
        self.gen_hierarchy: bool = False
        self.file: Optional[str] = None
        self.dir: Optional[str] = None
        self.model: str = 'llama3.1'
        self.temperature: float = 0.0

        self.parser: Parser = Parser()
        self.serializer: JSONSerializer = JSONSerializer()
        self.plantuml: PlantUML = PlantUML()
        self.retranslator: Retranslator = Retranslator()
        self.ai: AI = AI()

    def run(self) -> None:
        args: Namespace = self.args_parser.parse_args()
        for key, value in vars(args).items():
            setattr(self, key, value)

        if self.file is None:
            return

        if self.watch:
            self.watch_file(self.file)
        else:
            self.parse_file(self.file)

    def parse_file(self, file_path: str) -> None:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content: str = file.read()
                ontology, warnings = self.parser.parse(content, file_path)

                # Print warnings
                if warnings and not self.quiet:
                    print('\n\n'.join(warnings))

                if self.gen_hierarchy:
                    print('Generating hierarchy...')
                    hierarchy, comments = self.ai.generate_hierarchy(
                        ontology, self.model, self.temperature
                    )
                    ontology.hierarchy.extend(hierarchy)
                    print('\nGenerated relationships:')
                    for relationship, comment in zip(hierarchy, comments):
                        print(
                            f'{relationship.parent.name} {relationship.relationship.value} {relationship.children[0].name}: {comment}'
                        )

                base_dir = os.path.dirname(file_path)
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                output_dir = self.dir if self.dir is not None else base_dir

                os.makedirs(output_dir, exist_ok=True)

                ontologies: list[Ontology] = [ontology]
                base_names: list[str] = [base_name]

                for figure in ontology.figures:
                    ontologies.append(Ontology.from_figure(ontology, figure))
                    base_names.append(f'{base_name}_{figure.name}')

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
                    if not self.debug:
                        continue
                    retranslator_content: str = self.retranslator.translate(ontology)
                    retranslator_file_path: str = os.path.join(
                        output_dir, f'{base_name}_retr.ontol'
                    )
                    with open(
                        retranslator_file_path, 'w', encoding='utf-8'
                    ) as retr_file:
                        retr_file.write(retranslator_content)
        except Exception as e:
            print(e)

    def watch_file(self, file_path: str):
        self.parse_file(file_path)

        class FileChangeHandler(FileSystemEventHandler):
            def __init__(self, parse_callback):
                super().__init__()
                self.parse_callback = parse_callback

            def on_modified(self, event):
                if event.src_path.endswith('.ontol'):
                    print(f'File {event.src_path} modified, re-parsing...')
                    self.parse_callback(event.src_path)

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


def main():
    cli: CLI = CLI()
    cli.run()


if __name__ == '__main__':
    main()
