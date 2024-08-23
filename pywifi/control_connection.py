"""Module that controls Wi-Fi connect or disconnect."""

import logging
import os
import subprocess

from .model import ERRORS, process_err, settings


class ControlConnection:
    """Wrapper for Wi-Fi connection.

    >>> ControlConnection

    """

    def __init__(self, wifi_ssid: str = None, wifi_password: str = None, logger: logging.Logger = None):
        """Instantiates the object.

        Args:
            wifi_ssid: SSID of the Wi-Fi connection.
            wifi_password: Password for the Wi-Fi connection.
            logger: Bring your own logger.
        """
        self.wifi_ssid = wifi_ssid or settings.wifi_ssid
        self.wifi_password = wifi_password or settings.wifi_password
        if not self.wifi_ssid or not self.wifi_password:
            raise ValueError("'wifi_ssid' and 'wifi_password' are required.")

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

    def darwin_connector(self) -> bool:
        """Connects to Wi-Fi using SSID and password in env vars for macOS."""
        if not os.path.exists("/System/Library/Frameworks/CoreWLAN.framework"):
            self.logger.error("WLAN framework not found.")
            return False

        import objc  # macOS specific

        self.logger.info(f'Scanning for {self.wifi_ssid} in WiFi range')

        try:
            # noinspection PyUnresolvedReferences
            objc.loadBundle('CoreWLAN',
                            bundle_path='/System/Library/Frameworks/CoreWLAN.framework',
                            module_globals=globals())
        except ImportError as error:
            self.logger.error(error)
            return False

        interface = CWInterface.interface()  # noqa
        networks, error = interface.scanForNetworksWithName_error_(self.wifi_ssid, None)
        if not networks:
            self.logger.error(f'Failed to detect the SSID: {self.wifi_ssid}')
            self.logger.error(error) if error else None
            return False

        network = networks.anyObject()
        success, error = interface.associateToNetwork_password_error_(network, self.wifi_password, None)
        if success:
            self.logger.info(f'Connected to {self.wifi_ssid}')
            return True
        elif error:
            self.logger.error(f'Unable to connect to {self.wifi_ssid}')
            self.logger.error(error)

    def linux_connector(self) -> bool:
        """Connects to Wi-Fi using SSID and password in env vars for Linux."""
        cmd = f"{settings.nmcli} d wifi connect '{self.wifi_ssid}' password '{self.wifi_password}'"
        try:
            result = subprocess.check_output(cmd, shell=True)
        except ERRORS as error:
            process_err(error=error, logger=self.logger)
            return False
        self.logger.info(f'Connected to {self.wifi_ssid}')
        self.logger.debug(result.decode(encoding='UTF-8').strip())
        return True

    def win_connector(self) -> bool:
        """Connects to Wi-Fi using SSID and password in env vars for Windows."""
        self.logger.info(f'Connecting to {self.wifi_ssid} in WiFi range')
        command = f"{settings.netsh} wlan connect name=\"" + self.wifi_ssid + \
                  "\" ssid=\"" + self.wifi_ssid + \
                  "\" interface=Wi-Fi"
        try:
            output = subprocess.check_output(command, shell=True)
            result = output.decode(encoding="UTF-8").strip()
            self.logger.info(result)
        except ERRORS as error:
            result = process_err(error=error, logger=self.logger)
        if result == f'There is no profile "{self.wifi_ssid}" assigned to the specified interface.':
            return self.win_create_new_connection()
        elif result != "Connection request was completed successfully.":
            self.logger.critical(f"ATTENTION::{result}")
            return False
        return True

    def win_create_new_connection(self) -> bool:
        """Establish a new connection using a xml config for Windows."""
        import jinja2  # windows specific
        self.logger.info(f"Establishing a new connection to {self.wifi_ssid}")
        command = f"{settings.netsh} wlan add profile filename=\"" + self.wifi_ssid + ".xml\"" + " interface=Wi-Fi"
        rendered = jinja2.Template(settings.win_wifi_xml).render(WIFI_SSID=self.wifi_ssid,
                                                                 WIFI_PASSWORD=self.wifi_password)
        with open(f'{self.wifi_ssid}.xml', 'w') as file:
            file.write(rendered)
        try:
            result = subprocess.check_output(command, shell=True)
            self.logger.info(result.decode(encoding="UTF-8"))
            os.remove(f'{self.wifi_ssid}.xml')
            return True
        except ERRORS as error:
            process_err(error=error, logger=self.logger)
            os.remove(f'{self.wifi_ssid}.xml')

    def wifi_connector(self) -> bool:
        """Connects to the Wi-Fi SSID stored in env vars (OS-agnostic)."""
        if settings.operating_system == "Darwin":
            return self.darwin_connector()
        elif settings.operating_system == "Windows":
            return self.win_connector()
        elif settings.operating_system == "Linux":
            return self.linux_connector()
