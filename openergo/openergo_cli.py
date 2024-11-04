import datetime
import os
import sys
from typing import List

from colors import color

from openergo.config import Config, ConfigType
from openergo.graph import graph as opengraph
from openergo.local_storage import LocalStorage
from openergo.logger import logger
from openergo.secrets import LocalSecrets
from openergo.stdio_connection import StdioConnection
from openergo.version import get_version


class OpenergoCli:
    @property
    def prompt(self) -> str:
        return f"{color('openergo', fg='#33ff33')} {color('∵', fg='#33ff33')} "

    @property
    def intro(self) -> str:
        def format_date(sec: float) -> str:
            return datetime.datetime.fromtimestamp(sec).strftime("%b %d %Y, %H:%M:%S.%f")[:-3]

        def get_version_path() -> str:
            return os.path.dirname(os.path.abspath(__file__)) + "/version.py"

        version: str = get_version()
        timestamp: str = format_date(os.path.getmtime(get_version_path()))
        intro: str = f"openergo {version} ({timestamp})\nType help or ? to list commands."
        return str(color(intro, fg="#ffffff"))

    def stdio(self, ref: str, *args: str) -> int:
        try:
            config: ConfigType = Config.from_json(ref)

            if not sys.stdin.isatty():
                stdin_data = sys.stdin.read().strip()
                if stdin_data:
                    args = (stdin_data,) + args
            else:
                raise BrokenPipeError("No input message piped in through stdin")

            connection = StdioConnection()
            connection.consume(args[0], config=config, storage=LocalStorage(), secrets=LocalSecrets(), logger=logger)

        except Exception as err:
            print(f"*** {err}")
            raise err

        return 0

    def graph(self, keys: List[str], *args: str) -> int:
        opengraph(keys, list(args))
        return 0
