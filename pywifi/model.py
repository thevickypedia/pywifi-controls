import logging
import os
import platform
import subprocess
from typing import Tuple, Union

import dotenv

if os.path.isfile(".env"):
    dotenv.load_dotenv(dotenv_path=".env")

ERRORS: Tuple = (subprocess.CalledProcessError, subprocess.SubprocessError, FileNotFoundError,)


def process_err(error: Union[subprocess.CalledProcessError, subprocess.SubprocessError],
                logger: logging.Logger) -> str:
    """Logs errors along with return code and output based on type of error.

    Args:
        error: Takes any one of multiple subprocess errors as argument.
        logger: Logger object.

    Returns:
        str:
        Decoded version of the error message or an empty string.
    """
    if isinstance(error, subprocess.CalledProcessError):
        result = error.output.decode(encoding='UTF-8').strip()
        logger.error(f"[{error.returncode}]: {result}")
        return result
    else:
        logger.error(error)
        return ""


class Settings:
    """Wrapper for settings.

    >>> Settings

    """

    def __init__(self):
        """Loads all required args."""
        self.wifi_ssid: str = os.environ.get('WIFI_SSID') or os.environ.get('wifi_ssid')
        self.wifi_password: str = os.environ.get('WIFI_PASSWORD') or os.environ.get('wifi_password')
        self.operating_system: str = platform.system()
        if self.operating_system not in ("Linux", "Darwin", "Windows"):
            raise OSError(
                f"Package is unsupported in {self.operating_system!r}"
            )
        with open(os.path.join(os.path.dirname(__file__), 'win_wifi_config.xml')) as file:
            self.win_wifi_xml = file.read()


settings = Settings()
