import sys
from pathlib import Path


BASE_DIR = (
    Path(sys.executable).resolve().parent
    if getattr(sys, "frozen", False)
    else Path(__file__).resolve().parent.parent
)
CONFIG_PATH = BASE_DIR / 'config' / 'config.ini'
PROJECT_INFO = BASE_DIR / 'pyproject.toml'
