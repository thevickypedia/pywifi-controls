import logging
import os
import platform
import subprocess
from typing import Union, Tuple

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
    wifi_ssid: str = os.environ.get('WIFI_SSID') or os.environ.get('wifi_ssid')
    wifi_password: str = os.environ.get('WIFI_PASSWORD') or os.environ.get('wifi_password')
    operating_system: str = platform.system()
    if operating_system not in ("Linux", "Darwin", "Windows"):
        raise OSError(
            "Package is unsupported in %s" % operating_system
        )
    with open(os.path.join(os.path.dirname(__file__), 'win_wifi_config.xml')) as file:
        win_wifi_xml = file.read()


settings = Settings()
