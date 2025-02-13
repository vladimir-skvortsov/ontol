import argparse
import time
import os

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from parser import Parser
from serializer import JSONSerializer

class CLI:
  def __init__(self):
    self.args_parser = argparse.ArgumentParser(description='Ontol DSL Parser')
    self.args_parser.add_argument('file', type=str, help='Path to the .ontol file')
    self.args_parser.add_argument('--watch', action='store_true', help='Watch for changes in the file')

    self.parser = Parser()
    self.serializer = JSONSerializer()

  def run(self):
    args = self.args_parser.parse_args()

    if args.watch:
      self.watch_file(args.file)
    else:
      self.parse_file(args.file)

  def parse_file(self, file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
      content = file.read()
      ontology = self.parser.parse(content)

      json_content = self.serializer.serialize(ontology)
      json_file_path = os.path.splitext(file_path)[0] + '.json'
      with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json_file.write(json_content)

      print(f"Ontology parsed and saved to {json_file_path}")

  def watch_file(self, file_path):
    class FileChangeHandler(FileSystemEventHandler):
      def __init__(self, parse_callback):
        super().__init__()
        self.parse_callback = parse_callback

      def on_modified(self, event):
        print(event.src_path)
        if event.src_path.endswith('.ontol'):
          print(f"File {event.src_path} modified, re-parsing...")
          self.parse_callback(event.src_path)

    event_handler = FileChangeHandler(self.parse_file)

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
