import os
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from watchdog.observers.api import BaseObserver

from argparse import ArgumentParser, Namespace

from src.ontol import Parser, JSONSerializer, PlantUML


VERSION: str = os.getenv('ONTOL_VERSION', 'unknown')


class CLI:
    def __init__(self) -> None:
        self.args_parser: ArgumentParser = ArgumentParser(
            description='Ontol DSL Parser - A tool for parsing and visualizing ontology files written in the Ontol DSL.'
        )
        self.args_parser.add_argument(
            'file', type=str, help='Path to the .ontol file to be parsed.'
        )
        self.args_parser.add_argument(
            '--watch',
            action='store_true',
            help='Watch the specified file for changes and re-parse automatically.',
        )
        self.args_parser.add_argument(
            '--version',
            action='version',
            version=f'%(prog)s {VERSION}',
            help='Show the version of the program and exit.',
        )

        self.parser: Parser = Parser()
        self.serializer: JSONSerializer = JSONSerializer()
        self.plantuml: PlantUML = PlantUML()

    def run(self) -> None:
        args: Namespace = self.args_parser.parse_args()

        if args.watch:
            self.watch_file(args.file)
        else:
            self.parse_file(args.file)

    def parse_file(self, file_path: str) -> None:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content: str = file.read()
                ontology, warnings = self.parser.parse(content, file_path)

                # Print warnings
                if warnings:
                    print('\n\n'.join(warnings))

                # JSON
                json_content: str = self.serializer.serialize(ontology)
                json_file_path: str = os.path.splitext(file_path)[0] + '.json'
                with open(json_file_path, 'w', encoding='utf-8') as json_file:
                    json_file.write(json_content)

                # PlantUML
                plantuml_content: str = self.plantuml.generate(ontology)
                puml_file_path: str = os.path.splitext(file_path)[0] + '.puml'
                with open(puml_file_path, 'w', encoding='utf-8') as puml_file:
                    puml_file.write(plantuml_content)

                self.plantuml.processes_puml_to_png(puml_file_path)
        except Exception as e:
            print(e)

    def watch_file(self, file_path):
        self.parse_file(file_path)

        class FileChangeHandler(FileSystemEventHandler):
            def __init__(self, parse_callback):
                super().__init__()
                self.parse_callback = parse_callback

            def on_modified(self, event):
                if event.src_path.endswith('.ontol'):
                    print(f'File {event.src_path} modified, re-parsing...')
                    self.parse_callback(event.src_path)

        event_handler = FileChangeHandler(self.parse_file)

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
