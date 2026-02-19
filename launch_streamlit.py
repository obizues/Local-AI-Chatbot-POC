import os
import subprocess

project_root = os.path.dirname(os.path.abspath(__file__))
ui_app_path = os.path.join(project_root, 'ui', 'app.py')
streamlit_exe = os.path.join(project_root, '.venv', 'Scripts', 'streamlit.exe')

subprocess.run([streamlit_exe, "run", ui_app_path])
