"""
Device Under Test (DUT) Configuration Manager

This module provides classes to manage device configurations loaded from JSON files.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional


class DUTConfig:
    """
    Manages device configuration for a Device Under Test (DUT).

    Loads and provides access to device-specific settings including:
    - UART port mappings
    - Boot mode configurations
    - Health check settings
    - Power management configuration
    """

    def __init__(self, device_name: str, config_base_dir: Optional[Path] = None):
        """
        Initialize DUTConfig with a device name.

        Args:
            device_name: Name of the device (e.g., 'j721s2-evm-#001')
            config_base_dir: Base directory for device configs.
                           Defaults to <project_root>/config/devices/

        Raises:
            FileNotFoundError: If the configuration file doesn't exist
            json.JSONDecodeError: If the configuration file is not valid JSON
        """
        if config_base_dir is None:
            config_base_dir = Path.cwd() / "config" / "devices"

        self.device_name_input = device_name
        self.config_path = config_base_dir / f"{device_name}.json"
        self._config: Dict[str, Any] = {}
        self.load_config()

    def load_config(self) -> None:
        """
        Load configuration from the JSON file.

        Raises:
            FileNotFoundError: If the configuration file doesn't exist
            json.JSONDecodeError: If the configuration file is not valid JSON
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with open(self.config_path, 'r') as f:
            self._config = json.load(f)

    def reload_config(self) -> None:
        """Reload configuration from the file."""
        self.load_config()

    @property
    def device_name(self) -> str:
        """Get the device name."""
        return self._config.get('device_name', '')

    @property
    def device_type(self) -> str:
        """Get the device type."""
        return self._config.get('device_type', '')

    @property
    def uart_port_map(self) -> Dict[str, str]:
        """Get the complete UART port mapping."""
        return self._config.get('uart_port_map', {})

    def get_uart_port(self, port_name: str) -> Optional[str]:
        """
        Get UART port path for a specific port name.

        Args:
            port_name: Name of the port (e.g., 'mcu0', 'application', 'debug')

        Returns:
            UART port path (e.g., '/dev/ttyUSB0') or None if not found
        """
        return self.uart_port_map.get(port_name)

    def get_default_uart_port(self) -> Optional[str]:
        """Get the default UART port."""
        return self.get_uart_port('default')

    @property
    def boot_mode_map(self) -> Dict[str, str]:
        """Get the complete boot mode mapping."""
        return self._config.get('boot_mode_map', {})

    def get_boot_mode(self, mode_name: str) -> Optional[str]:
        """
        Get boot mode value for a specific mode name.

        Args:
            mode_name: Name of the boot mode (e.g., 'uart', 'emmc', 'sd_card')

        Returns:
            Boot mode value (e.g., '000E') or None if not found
        """
        return self.boot_mode_map.get(mode_name)

    def get_default_boot_mode(self) -> Optional[str]:
        """Get the default boot mode."""
        return self.get_boot_mode('default')

    @property
    def health_check(self) -> Dict[str, Any]:
        """Get health check configuration."""
        return self._config.get('health_check', {})

    @property
    def health_check_uart_ports(self) -> list:
        """Get list of UART ports to check for health monitoring."""
        return self.health_check.get('uart_ports', [])

    @property
    def health_check_interval(self) -> int:
        """Get health check interval in seconds."""
        return self.health_check.get('check_interval_seconds', 60)

    @property
    def health_check_error_threshold(self) -> int:
        """Get health check error threshold."""
        return self.health_check.get('error_threshold', 5)

    @property
    def power_config(self) -> Dict[str, Any]:
        """Get complete power configuration."""
        return self._config.get('power_config', {})

    def get_power_module(self) -> str:
        """Get the power control module name."""
        return self.power_config.get('module', '')

    def get_power_settings(self) -> Dict[str, Any]:
        """Get power module settings."""
        return self.power_config.get('settings', {})

    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        return self._config.get(key, default)

    def to_dict(self) -> Dict[str, Any]:
        """
        Get the complete configuration as a dictionary.

        Returns:
            Complete configuration dictionary
        """
        return self._config.copy()

    def __repr__(self) -> str:
        """String representation of DUTConfig."""
        return f"DUTConfig(device_name='{self.device_name}', device_type='{self.device_type}')"

    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"DUT: {self.device_name} ({self.device_type})"
