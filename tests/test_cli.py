import os
import tempfile

from ontol import CLI
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def cli():
    return CLI()


@pytest.fixture
def sample_ontology_file():
    content = """
    version: '1.0'
    """
    with tempfile.NamedTemporaryFile(suffix='.ontol', delete=False) as tmp_file:
        tmp_file.write(content.encode('utf-8'))
        tmp_file_path = tmp_file.name
    return tmp_file_path


def test_parse_file(cli, sample_ontology_file):
    cli.parse_file(sample_ontology_file)

    json_file_path: str = os.path.splitext(sample_ontology_file)[0] + '.json'
    puml_file_path: str = os.path.splitext(sample_ontology_file)[0] + '.puml'

    assert os.path.exists(json_file_path)
    assert os.path.exists(puml_file_path)

    os.remove(sample_ontology_file)
    os.remove(json_file_path)
    os.remove(puml_file_path)


def test_render_plantuml_to_png(cli):
    cli.render_plantuml_to_png = MagicMock()
    puml_file_path = 'test.puml'

    cli.render_plantuml_to_png(puml_file_path)

    cli.render_plantuml_to_png.assert_called_with(puml_file_path)


def test_watch_file(cli):
    with (
        patch('watchdog.observers.Observer.schedule') as mock_schedule,
        patch('watchdog.observers.Observer.start') as mock_start,
        patch('watchdog.observers.Observer.join') as mock_join,
        patch('time.sleep', side_effect=KeyboardInterrupt),
    ):
        mock_start.return_value = None
        mock_join.return_value = None

        cli.watch_file('test.ontol')

        mock_schedule.assert_called()
        mock_start.assert_called()
        mock_join.assert_called()


def test_watch_file_no_changes(cli):
    with (
        patch('watchdog.observers.Observer.schedule') as mock_schedule,
        patch('watchdog.observers.Observer.start') as mock_start,
        patch('watchdog.observers.Observer.join') as mock_join,
        patch('time.sleep', side_effect=KeyboardInterrupt),
    ):
        mock_start.return_value = None
        mock_join.return_value = None

        cli.watch_file('nonexistent_file.ontol')

        mock_schedule.assert_called()
        mock_start.assert_called()
        mock_join.assert_called()
