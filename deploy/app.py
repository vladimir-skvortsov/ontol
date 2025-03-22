import streamlit as st
import subprocess
import shutil
import os
import uuid
from zipfile import ZipFile

st.set_page_config(layout='wide')

DEFAULT_TEXT = """version: '1.0'
title: ''
author: ''
description: ''

types:

functions:

hierarchy:
"""

if 'session_id' not in st.session_state:
    st.session_state['session_id'] = str(uuid.uuid4())
    st.session_state['first_load'] = True
    st.session_state['auto_compile'] = False


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


USER_RESULTS_DIR = f'results/{st.session_state["session_id"]}'
ZIP_FILE = f'{USER_RESULTS_DIR}.zip'


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


def on_change():
    st.session_state['auto_compile'] = True


if st.session_state['first_load']:
    st.session_state['first_load'] = False
    st.session_state['auto_compile'] = True

st.title('Ontol DSL Online REPL')

col1, col2 = st.columns(2)

with col1:
    code = st.text_area(
        'Enter DSL Code',
        label_visibility='collapsed',
        height=800,
        value=DEFAULT_TEXT,
        on_change=on_change,
    )

compile_now = st.button('Generate Image', icon='🖼')

if compile_now or st.session_state['auto_compile']:
    st.session_state['auto_compile'] = False
    if code.strip():
        try:
            logs = generate_image(code)
            image_path = os.path.join(USER_RESULTS_DIR, 'ontology.png')
            with col2:
                st.image(
                    image_path, use_container_width=True, caption='Generated image'
                )
        except Exception as e:
            st.error(f'Error generating image: {e}')
        finally:
            with st.expander('Execution Logs (click to expand)'):
                st.text(logs)
    else:
        st.warning('Please enter DSL code.')

zip_path = os.path.join(USER_RESULTS_DIR, 'results.zip')
if os.path.exists(zip_path):
    with open(zip_path, 'rb') as f:
        st.download_button(
            'Download Results as ZIP',
            f,
            file_name='results.zip',
            mime='application/zip',
        )
    rm_dir(USER_RESULTS_DIR)
