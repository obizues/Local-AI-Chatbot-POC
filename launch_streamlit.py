import os
import sys
import subprocess

# Set working directory to the directory containing this script (project root)
project_root = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_root)

# Optionally add project root to sys.path for module resolution
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Launch Streamlit app using absolute path and print output/errors
app_path = os.path.join(project_root, 'ui', 'app.py')
print(f"[INFO] Attempting to launch Streamlit app at: {app_path}")
if not os.path.isfile(app_path):
    print(f"[ERROR] App file does not exist: {app_path}")
    sys.exit(1)
try:
    print("[INFO] Running: streamlit run {0}".format(app_path))
    result = subprocess.run(f'streamlit run "{app_path}"', shell=True, capture_output=True, text=True)
    print("[INFO] Streamlit process finished.")
    print("[STDOUT]\n" + result.stdout)
    print("[STDERR]\n" + result.stderr)
    if result.returncode != 0:
        print(f"[ERROR] Streamlit exited with code {result.returncode}")
        sys.exit(result.returncode)
except Exception as e:
    print(f"[ERROR] Exception while running Streamlit: {e}")
    sys.exit(1)