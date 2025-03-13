import os
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from watchdog.observers.api import BaseObserver

from argparse import ArgumentParser, Namespace

from ontol import Parser, JSONSerializer, PlantUML, Retranslator


__VERSION__ = os.getenv('ONTOL_VERSION', 'dev')


class CLI:
    def __init__(self) -> None:
        self.args_parser: ArgumentParser = ArgumentParser(
            description='Ontol DSL Parser - A tool for parsing and visualizing ontology files written in the Ontol DSL.'
        )
        self.args_parser.add_argument(
            'file', type=str, help='Path to the .ontol file to be parsed.'
        )
        self.args_parser.add_argument(
            '-w',
            '--watch',
            action='store_true',
            help='Watch the specified file for changes and re-parse automatically.',
        )
        self.args_parser.add_argument(
            '-d',
            '--debug',
            action='store_true',
            help='Get retranslation version of the file .ontol.',
        )
        self.args_parser.add_argument(
            '-v',
            '--version',
            action='version',
            version=f'%(prog)s {__VERSION__}',
            help='Show the version of the program and exit.',
        )
        self.args_parser.add_argument(
            '-q',
            '--quiet',
            action='store_true',
            help='Ignore all the warnings.',
        )

        self.parser: Parser = Parser()
        self.serializer: JSONSerializer = JSONSerializer()
        self.plantuml: PlantUML = PlantUML()
        self.retranslator: Retranslator = Retranslator()

    def run(self) -> None:
        args: Namespace = self.args_parser.parse_args()

        debug: bool = True if args.debug else False
        quiet: bool = True if args.quiet else False

        if args.watch:
            self.watch_file(args.file, debug, quiet)
        else:
            self.parse_file(args.file, debug, quiet)

    def parse_file(
        self, file_path: str, debug: bool = False, quiet: bool = False
    ) -> None:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content: str = file.read()
                ontology, warnings = self.parser.parse(content, file_path)

                # Print warnings
                if warnings and not quiet:
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

                # Retranslator
                if not debug:
                    return
                retranslator_content: str = self.retranslator.translate(ontology)
                retranslator_file_path: str = (
                    os.path.splitext(file_path)[0] + '_retr' + '.ontol'
                )
                with open(retranslator_file_path, 'w', encoding='utf-8') as retr_file:
                    retr_file.write(retranslator_content)
        except Exception as e:
            print(e)

    def watch_file(self, file_path, debug: bool = False, quiet: bool = False):
        self.parse_file(file_path, debug, quiet)

        class FileChangeHandler(FileSystemEventHandler):
            def __init__(self, parse_callback):
                super().__init__()
                self.parse_callback = parse_callback

            def on_modified(self, event):
                if event.src_path.endswith('.ontol'):
                    print(f'File {event.src_path} modified, re-parsing...')
                    self.parse_callback(event.src_path, debug, quiet)

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
