import argparse
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

class OntolCLI:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description='Ontol DSL Parser')
        self.parser.add_argument('file', type=str, help='Path to the .ontol file')
        self.parser.add_argument('--watch', action='store_true', help='Watch for changes in the file')

    def run(self):
        args = self.parser.parse_args()

        if args.watch:
            self.watch_file(args.file)
        else:
            self.parse_file(args.file)

    def parse_file(self, file_path):
        # Логика парсинга файла
        print(f"Parsing file: {file_path}")

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
    cli = OntolCLI()
    cli.run()
