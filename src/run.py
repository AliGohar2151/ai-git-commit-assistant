# run.py
import streamlit.web.cli as stcli
import os
import pathlib
import sys

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

if __name__ == '__main__':
    # The 'app.py' needs to be found by the executable
    app_path = str(pathlib.Path(get_resource_path('app.py')))

    # Construct the arguments for Streamlit
    args = [
        "run", app_path,
        "--global.developmentMode=false",
        "--server.headless=true",  # Recommended for executables
    ]
    sys.argv = ["streamlit", *args]
    sys.exit(stcli.main())
