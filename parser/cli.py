import argparse
import time
import os

from plantuml import PlantUML

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from parser import Parser
from serializer import JSONSerializer
from plantuml_generator import PlantUMLGenerator


class CLI:
  def __init__(self):
    self.args_parser = argparse.ArgumentParser(
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

    self.parser = Parser()
    self.serializer = JSONSerializer()
    self.plantuml_generator = PlantUMLGenerator()

  def run(self):
    args = self.args_parser.parse_args()

    if args.watch:
      self.watch_file(args.file)
    else:
      self.parse_file(args.file)

  def parse_file(self, file_path):
    with open(file_path, "r", encoding="utf-8") as file:
      content = file.read()
      ontology = self.parser.parse(content)

      # JSON
      json_content = self.serializer.serialize(ontology)
      json_file_path = os.path.splitext(file_path)[0] + ".json"
      with open(json_file_path, "w", encoding="utf-8") as json_file:
        json_file.write(json_content)

      # PlantUML
      plantuml_content = self.plantuml_generator.generate(ontology)
      puml_file_path = os.path.splitext(file_path)[0] + ".puml"
      with open(puml_file_path, "w", encoding="utf-8") as puml_file:
        puml_file.write(plantuml_content)

      self.render_plantuml_to_png(puml_file_path)

  def render_plantuml_to_png(self, puml_file_path):
    server = PlantUML(url="http://www.plantuml.com/plantuml/img/")
    server.processes_file(puml_file_path)

  def watch_file(self, file_path):
    class FileChangeHandler(FileSystemEventHandler):
      def __init__(self, parse_callback):
        super().__init__()
        self.parse_callback = parse_callback

      def on_modified(self, event):
        if event.src_path.endswith(".ontol"):
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
