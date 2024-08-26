import logging
import os
import platform
import subprocess
from typing import Any, Tuple, Union

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


class Commands:
    """Wrapper for OS specific commands.

    >>> Commands

    """

    nmcli: str = "/usr/bin/nmcli"  # Linux
    networksetup: str = "/usr/sbin/networksetup"  # macOS
    netsh: str = "C:\\Windows\\System32\\netsh.exe"  # Windows


commands = Commands()


def get_env(key: str, default: Any = None, alias: str = None):
    """Get environment variable (case insensitive) with default and alias options.

    Args:
        key: Key of the enviornment variable.
        default: Default value in case key is not found in env var. Defaults to None.
        alias: Alias key. Defaults to None.

    See Also:
        Order of execution:
            1. key
            2. alias
            3. default
    """
    if os.environ.get("PyWifi-Sphinx"):
        return None
    if (value := os.environ.get(key.lower()) or os.environ.get(key.upper())):
        return value
    if alias:
        if (value := os.environ.get(alias.lower()) or os.environ.get(alias.upper())):
            return value
    return default


class Settings:
    """Wrapper for settings.

    >>> Settings

    """

    root_pass: str = get_env("root_pass", alias="password")
    wifi_ssid: str = get_env("wifi_ssid")
    wifi_password: str = get_env("wifi_password")
    nmcli: str = get_env("nmcli", default=commands.nmcli)
    netsh: str = get_env("netsh", default=commands.netsh)
    networksetup: str = get_env("networksetup", default=commands.networksetup)


settings = Settings()
settings.operating_system = platform.system()
if settings.operating_system not in ("Linux", "Darwin", "Windows"):
    raise OSError(
        f"Package is unsupported in {settings.operating_system!r}"
    )
with open(os.path.join(os.path.dirname(__file__), 'win_wifi_config.xml')) as file:
    settings.win_wifi_xml = file.read()
