import streamlit as st
import subprocess
import shutil
import os
import uuid
from zipfile import ZipFile
from code_editor import code_editor

st.set_page_config(page_title='Ontol DSL Online REPL', layout='wide')

DEFAULT_TEXT = """version: '1.0'
title: 'Set theory'
author: ''
description: ''

types:
element: 'Element', '', { color: '#E6B8B7' }
set: 'Set\n\n\n\n\n', '', { color: '#E6B8B7' }
subset: 'Subset', '', { color: '#E6B8B7' }

functions:
add: 'Add' (set: '', element: '') -> set: '', { color: '#D0FFD0', colorArrow: '#red' }
remove: 'Remove' (set: '', element: '') -> set: '', { color: '#D0FFD0', colorArrow: '#blue' }

union: 'Объединение' (set: '') -> set: '', { color: '#D0FFD0', inputTitle: '*' }
intersect: 'Пересечение' (set: '') -> set: '', { color: '#D0FFD0', inputTitle: '*' }
difference: 'Разность' (set: '', set: '') -> set: '', { color: '#D0FFD0' }
symDiff: 'Симметрическая разность' (set: '', set: '') -> set: '', { color: '#D0FFD0' }

hierarchy:
element aggregation set, { leftChar: '*' }
subset inheritance set
"""
SNIPPETS = [
    {
        'name': 'types block',
        'code': 'types:\n',
    },
    {
        'name': 'type definition',
        'code': "name: '', ''",
    },
    {
        'name': 'type definition with arguments',
        'code': "name: '', '', {\n\n}",
    },
    {
        'name': 'functions block',
        'code': 'functions:\n',
    },
    {
        'name': 'function definition',
        'code': "name: '' (arg1: '', arg2: '') -> return_type",
    },
    {
        'name': 'function definition with arguments',
        'code': "name: '' (arg1: '', arg2: '') -> return_type, {\n\n}",
    },
    {
        'name': 'hierarchy block',
        'code': 'heirarchy:\n',
    },
    {
        'name': 'relationship definition',
        'code': 'parent aggregation child',
    },
    {
        'name': 'relationship definition with arguments',
        'code': 'parent aggregation child, {\n\n}',
    },
]

if 'session_id' not in st.session_state:
    st.session_state['session_id'] = str(uuid.uuid4())
    st.session_state['first_load'] = True

USER_RESULTS_DIR = f'results/{st.session_state["session_id"]}'
ZIP_FILE = f'{USER_RESULTS_DIR}.zip'


def get_ontol_version():
    try:
        version = subprocess.check_output(['ontol', '--version'], text=True).strip()
        return version
    except Exception as e:
        return f'Ошибка получения версии: {e}'


def create_zip(directory):
    zip_filename = os.path.join(directory, 'results.zip')
    with ZipFile(zip_filename, 'w') as zipf:
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                if file == 'results.zip':
                    continue
                arcname = os.path.relpath(file_path, directory)
                zipf.write(file_path, arcname)
    return zip_filename


def rm_dir(dir: str):
    if os.path.exists(dir):
        shutil.rmtree(dir)


def generate_image(dsl_text):
    os.makedirs(USER_RESULTS_DIR, exist_ok=True)
    input_file = os.path.join(USER_RESULTS_DIR, 'ontology.ontol')

    with open(input_file, 'w') as f:
        f.write(dsl_text)

    process = subprocess.Popen(
        ['ontol', input_file, '--output-dir', USER_RESULTS_DIR],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    logs = []
    for line in process.stdout:
        logs.append(line.strip())

    process.wait()

    create_zip(USER_RESULTS_DIR)
    return '\n'.join(logs)


if 'version' not in st.session_state:
    st.session_state['version'] = get_ontol_version()

st.title('Ontol DSL Online REPL')
st.markdown(f'`{st.session_state["version"]}`')

col1, col2 = st.columns(2)

with col1:
    response_dict = code_editor(
        DEFAULT_TEXT,
        height=[20, 30],
        focus=True,
        options={'showLineNumbers': True},
        lang='plain_text',
        snippets=[SNIPPETS, ''],
        response_mode='debounce',
    )
    code = DEFAULT_TEXT if st.session_state['first_load'] else response_dict['text']

button_col1, button_col2 = st.columns([1, 1])

with button_col1:
    st.button('Generate image', icon='🖼', use_container_width=True)

try:
    logs = generate_image(code)
    image_path = os.path.join(USER_RESULTS_DIR, 'ontology.png')
    with col2:
        st.image(image_path, use_container_width=True)
except Exception as e:
    st.error(f'Error generating image: {e}')
finally:
    with st.expander('Execution logs (click to expand)'):
        st.text(logs)

zip_path = os.path.join(USER_RESULTS_DIR, 'results.zip')
if os.path.exists(zip_path):
    with button_col2:
        with open(zip_path, 'rb') as f:
            st.download_button(
                'Download compiled files',
                f,
                file_name='results.zip',
                mime='application/zip',
                icon='📥',
                use_container_width=True,
            )
        rm_dir(USER_RESULTS_DIR)

if st.session_state['first_load']:
    st.session_state['first_load'] = False

rm_dir(USER_RESULTS_DIR)
