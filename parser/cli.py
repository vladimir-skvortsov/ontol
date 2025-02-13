import argparse
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from parser import Parser

class CLI:
    def __init__(self):
        self.args_parser = argparse.ArgumentParser(description='Ontol DSL Parser')
        self.args_parser.add_argument('file', type=str, help='Path to the .ontol file')
        self.args_parser.add_argument('--watch', action='store_true', help='Watch for changes in the file')
        self.parser = Parser()

    def run(self):
        args = self.args_parser.parse_args()

        if args.watch:
            self.watch_file(args.file)
        else:
            self.parse_file(args.file)

    def parse_file(self, file_path):
        print(f"Parsing file: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            ontology = self.parser.parse(content)
            print(ontology)

    def watch_file(self, file_path):
        event_handler = FileSystemEventHandler()
        event_handler.on_modified = lambda event: self.parse_file(file_path)

        observer = Observer()
        observer.schedule(event_handler, path=file_path, recursive=False)
        observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

if __name__ == "__main__":
    cli = CLI()
    cli.run()
