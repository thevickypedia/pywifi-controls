"""Module that controls toggling Wi-Fi on or off."""

import logging
import subprocess
from typing import Union

from .model import ERRORS, process_err, settings


def get_connection_info(logger: logging.Logger, target: str = "SSID") -> Union[str, None]:
    """Gets information about the network connected.

    Returns:
        str:
        Wi-Fi or Ethernet SSID or Name.
    """
    try:
        if settings.operating_system == "Darwin":
            process = subprocess.Popen(
                ["/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport", "-I"],
                stdout=subprocess.PIPE
            )
        elif settings.operating_system == "Windows":
            process = subprocess.check_output(f"{settings.netsh} wlan show interfaces", shell=True)
        elif settings.operating_system == "Linux":
            process = subprocess.check_output(f"{settings.nmcli} -t -f name connection show --active | head -n 1",
                                              shell=True)
        else:
            return
    except (subprocess.CalledProcessError, subprocess.CalledProcessError, FileNotFoundError) as error:
        if isinstance(error, subprocess.CalledProcessError):
            result = error.output.decode(encoding='UTF-8').strip()
            logger.error(f"[{error.returncode}]: {result}")
        else:
            logger.error(error)
        return
    if settings.operating_system == "Darwin":
        out, err = process.communicate()
        if error := process.returncode:
            logger.error(f"Failed to fetch {target} with exit code: {error}\n{err}")
            return
        # noinspection PyTypeChecker
        return dict(map(str.strip, info.split(": ")) for info in out.decode("utf-8").splitlines()[:-1] if
                    len(info.split()) == 2).get(target)
    elif settings.operating_system == "Windows":
        if result := [i.decode().strip() for i in process.splitlines() if
                      i.decode().strip().startswith(target)]:
            return result[0].split(':')[-1].strip()
        else:
            logger.error(f"Failed to fetch {target}")
    else:
        if process:
            return process.decode(encoding='UTF-8').strip()


class ControlPeripheral:
    """Initiates ControlPeripheral to toggle Wi-Fi on or off.

    >>> ControlPeripheral

    """

    def __init__(self, name: str = None, logger: logging.Logger = None):
        """Instantiates the object.

        Args:
            name: Takes the name of the peripheral connection.
            logger: Bring your own logger.
        """
        # Log config
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)
            log_handler = logging.StreamHandler()
            log_handler.setFormatter(fmt=logging.Formatter(
                fmt='%(asctime)s - %(levelname)s - [%(module)s:%(lineno)d] - %(funcName)s - %(message)s',
                datefmt='%b-%d-%Y %I:%M:%S %p'
            ))
            self.logger.addHandler(hdlr=log_handler)
            self.logger.setLevel(level=logging.DEBUG)
        self.name = name or get_connection_info(target='Name', logger=self.logger) or "Wi-Fi"

    def darwin_enable(self) -> None:
        """Enables Wi-Fi on macOS."""
        try:
            result = subprocess.check_output(f"{settings.networksetup} -setairportpower airport on", shell=True)
            self.logger.info(' '.join(result.decode(encoding="UTF-8").splitlines()))
        except ERRORS as error:
            process_err(error=error, logger=self.logger)

    def darwin_disable(self) -> None:
        """Disables Wi-Fi on macOS."""
        try:
            result = subprocess.check_output(f"{settings.networksetup} -setairportpower airport off", shell=True)
            self.logger.info(' '.join(result.decode(encoding="UTF-8").splitlines()))
        except ERRORS as error:
            process_err(error=error, logger=self.logger)

    def linux_enable(self) -> None:
        """Enables Wi-Fi on Linux."""
        if settings.root_pass:
            cmd = f"echo {settings.root_pass} | sudo -S {settings.nmcli} radio wifi on"
        else:
            cmd = f"{settings.nmcli} radio wifi on"
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            if result.returncode:
                self.logger.error("Failed to enable Wi-Fi - %s", result.returncode)
                if decoded_stderr := result.stderr.decode('utf-8'):
                    self.logger.error(f"stderr: {decoded_stderr}")
            else:
                self.logger.info("Wi-Fi has been enabled.")
                if decoded_stdout := result.stdout.decode('utf-8'):
                    self.logger.debug(f"stdout: {decoded_stdout}")
            return result.returncode == 0
        except ERRORS as error:
            process_err(error=error, logger=self.logger)

    def linux_disable(self) -> None:
        """Disables Wi-Fi on Linux."""
        if settings.root_pass:
            cmd = f"echo {settings.root_pass} | sudo -S {settings.nmcli} radio wifi off"
        else:
            cmd = f"{settings.nmcli} radio wifi off"
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            if result.returncode:
                self.logger.error("Failed to disable Wi-Fi - %s", result.returncode)
                if decoded_stderr := result.stderr.decode('utf-8'):
                    self.logger.error(f"stderr: {decoded_stderr}")
            else:
                self.logger.info("Wi-Fi has been disabled.")
                if decoded_stdout := result.stdout.decode('utf-8'):
                    self.logger.debug(f"stdout: {decoded_stdout}")
            return result.returncode == 0
        except ERRORS as error:
            process_err(error=error, logger=self.logger)

    def win_enable(self) -> None:
        """Enables Wi-Fi on Windows."""
        try:
            result = subprocess.check_output(f"{settings.netsh} interface set interface {self.name!r} enabled",
                                             shell=True)
            if result := result.decode(encoding="UTF-8"):
                self.logger.error(result)
            else:
                self.logger.info(f"{self.name} has been enabled.")
        except ERRORS as error:
            process_err(error=error, logger=self.logger)

    def win_disable(self) -> None:
        """Disables Wi-Fi on Windows."""
        try:
            result = subprocess.check_output(f"{settings.netsh} interface set interface {self.name!r} disabled",
                                             shell=True)
            result = result.decode(encoding="UTF-8").strip()
            if result:
                self.logger.error(result)
            else:
                self.logger.info(f"{self.name} has been disabled.")
        except ERRORS as error:
            process_err(error=error, logger=self.logger)

    def enable(self) -> None:
        """Enable Wi-Fi (OS-agnostic)."""
        if settings.operating_system == "Darwin":
            self.darwin_enable()
        elif settings.operating_system == "Windows":
            self.win_enable()
        else:
            self.linux_enable()

    def disable(self) -> None:
        """Disable Wi-Fi (OS-agnostic)."""
        if settings.operating_system == "Darwin":
            self.darwin_disable()
        elif settings.operating_system == "Windows":
            self.win_disable()
        else:
            self.linux_enable()
