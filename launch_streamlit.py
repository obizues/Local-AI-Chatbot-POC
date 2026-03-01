import os
import subprocess
import sys

project_root = os.path.dirname(os.path.abspath(__file__))
ui_app_path = os.path.join(project_root, 'ui', 'app.py')
streamlit_exe = os.path.join(project_root, '.venv', 'bin', 'streamlit')

if not os.path.exists(streamlit_exe):
	print(f"ERROR: {streamlit_exe} not found. Did you install Streamlit in your virtual environment?")
	sys.exit(1)

try:
	print(f"Launching Streamlit app: {streamlit_exe} run {ui_app_path}")
	result = subprocess.run([streamlit_exe, "run", ui_app_path])
	print(f"Streamlit exited with return code: {result.returncode}")
except KeyboardInterrupt:
	print("[DEBUG] KeyboardInterrupt caught in launch_streamlit.py (not from user?)")
except Exception as e:
	print(f"[DEBUG] Exception occurred: {e}")
finally:
	print("[DEBUG] launch_streamlit.py finished.")