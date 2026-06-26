import configparser
import tomllib
from pathlib import Path

from core import BASE_DIR, CONFIG_PATH, PROJECT_INFO

fonts_dir = BASE_DIR / 'config' / 'fonts'
logos_dir = BASE_DIR / 'config' / 'logos'
templates_dir = BASE_DIR / 'config' / 'templates'

def load_config() -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH, encoding='utf-8')
    return config


def load_project_info():
    with open(PROJECT_INFO, "rb") as f:  # 注意：tomllib 需要以二进制模式（"rb"）打开文件
        data = tomllib.load(f)
    return data
