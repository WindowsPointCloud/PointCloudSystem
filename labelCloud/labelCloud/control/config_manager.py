"""Load configuration from .ini file."""

import configparser
from pathlib import Path
from typing import List, Union
import os
import sys
import pkg_resources


class ExtendedConfigParser(configparser.ConfigParser):
    """Extends the ConfigParser with the ability to read and parse lists.

    Can automatically parse float values besides plain strings.
    """

    def getlist(
        self, section, option, raw=False, vars=None, fallback=None
    ) -> Union[List[str], List[float], str]:
        raw_value = self.get(section, option, raw=raw, vars=vars, fallback=fallback)
        if "," in raw_value:
            values = [x.strip() for x in raw_value.split(",")]
            try:
                return [float(item) for item in values]
            except ValueError:
                return values
        return raw_value

    def getpath(self, section, option, raw=False, vars=None, fallback=None) -> Path:
        """Get a path from the configuration file."""
        return Path(self.get(section, option, raw=raw, vars=vars, fallback=fallback))


class ConfigManager(object):


#    PATH_TO_CONFIG = Path.cwd().joinpath("config.ini")
#
 #   PATH_TO_DEFAULT_CONFIG = Path(
 #      pkg_resources.resource_filename("labelCloud.resources", "default_config.ini")
 #  )

    def __init__(self) -> None:
        self.config = ExtendedConfigParser(comment_prefixes="/", allow_no_value=True)
        self._set_paths()
        self.read_from_file()
        
    def _set_paths(self) -> None:
        """ Set the paths for configuration files based on the runtime environment. """
        try:
            # PyInstaller creates a temp folder and stores path in `sys._MEIPASS`
            self.base_path = sys._MEIPASS
            print(f"Running in PyInstaller bundle. Base path: {self.base_path}")
        except AttributeError:
            # In a normal Python environment
            self.base_path = os.path.dirname(__file__)
            print(f"Running in normal Python environment. Base path: {self.base_path}")
            
        # Paths to configuration files
        self.PATH_TO_CONFIG = Path.cwd().joinpath("config.ini")
        self.PATH_TO_DEFAULT_CONFIG = Path(self.base_path).joinpath("resources", "default_config.ini")
        print(f"Config paths: {self.PATH_TO_CONFIG}, {self.PATH_TO_DEFAULT_CONFIG}")
        
    def read_from_file(self) -> None:
        if self.PATH_TO_CONFIG.is_file():
            print(f"Reading config from: {self.PATH_TO_CONFIG}")
            self.config.read(self.PATH_TO_CONFIG)
        else:
            print(f"Config file not found. Reading default config from: {self.PATH_TO_DEFAULT_CONFIG}")
            self.config.read(self.PATH_TO_DEFAULT_CONFIG)

    def write_into_file(self) -> None:
        with self.PATH_TO_CONFIG.open("w") as configfile:
            self.config.write(configfile, space_around_delimiters=True)

    def reset_to_default(self) -> None:
        self.config.read(self.PATH_TO_DEFAULT_CONFIG)

    def get_file_settings(self, key: str) -> str:
        return self.config["FILE"][key]


config_manager = ConfigManager()
config = config_manager.config
