import os
import glob
import subprocess
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class UARTDevice:
    devnode: str
    serial: Optional[str]
    vendor_id: Optional[str]
    product_id: Optional[str]
    manufacturer: Optional[str]
    product: Optional[str]


class UARTUdevManager:
    """
    Enumerates ttyUSB* / ttyACM* devices and generates udev rules
    for stable UART naming based on USB serial numbers.
    """

    def __init__(self):
        self.context = pyudev.Context()

    def list_uart_devices(self) -> List[UARTDevice]:
        devices = []

        for device in self.context.list_devices(subsystem="tty"):
            if not device.device_node:
                continue

            if not (
                device.device_node.startswith("/dev/ttyUSB")
                or device.device_node.startswith("/dev/ttyACM")
            ):
                continue

            usb_parent = device.find_parent("usb", "usb_device")
            if not usb_parent:
                continue

            devices.append(
                UARTDevice(
                    devnode=device.device_node,
                    serial=usb_parent.attributes.get("serial"),
                    vendor_id=usb_parent.attributes.get("idVendor"),
                    product_id=usb_parent.attributes.get("idProduct"),
                    manufacturer=usb_parent.attributes.get("manufacturer"),
                    product=usb_parent.attributes.get("product"),
                )
            )

        return devices

    def generate_udev_rule(
        self,
        serial: str,
        symlink_name: str,
        vendor_id: Optional[str] = None,
        product_id: Optional[str] = None,
    ) -> str:
        """
        Generate a udev rule that creates /dev/<symlink_name>
        """

        rule = (
            'SUBSYSTEM=="tty", '
            'ATTRS{serial}=="{serial}", '
        )

        if vendor_id:
            rule += f'ATTRS{{idVendor}}=="{vendor_id}", '
        if product_id:
            rule += f'ATTRS{{idProduct}}=="{product_id}", '

        rule += f'SYMLINK+="{symlink_name}"'

        return rule

    def write_udev_rules(
        self,
        rules: List[str],
        filename: str = "/etc/udev/rules.d/99-uart-names.rules",
    ):
        if os.geteuid() != 0:
            raise PermissionError("Must be run as root to write udev rules")

        with open(filename, "w") as f:
            for rule in rules:
                f.write(rule + "\n")

        subprocess.run(["udevadm", "control", "--reload-rules"], check=True)
        subprocess.run(["udevadm", "trigger"], check=True)


class UartService:
    def __init__(self):
        pass

    def list_uart_ports(self):
        """
        List all /dev/ttyUSB* and /dev/ttyACM* ports with their serial numbers (if available).
        Returns a list of dicts: [{ 'port': '/dev/ttyUSB0', 'serial': 'XXXX' }, ...]
        """
        ports = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
        result = []
        for port in ports:
            serial = None
            try:
                # Find the device symlink in /sys/class/tty
                tty_path = os.path.realpath(f'/sys/class/tty/{os.path.basename(port)}')
                # Walk up to the USB device directory
                dev_path = tty_path
                for _ in range(5):
                    if os.path.exists(os.path.join(dev_path, 'serial')):
                        break
                    dev_path = os.path.dirname(dev_path)
                serial_file = os.path.join(dev_path, 'serial')
                if os.path.exists(serial_file):
                    with open(serial_file, 'r') as f:
                        serial = f.read().strip()
            except Exception:
                serial = None
            result.append({'port': port, 'serial': serial})
        return result

    def set_udev_rules(self, serial, name):
        """
        Set a udev rule to create a symlink /dev/<name> for the UART device with the given serial number.
        Args:
            serial (str): Serial number of the device
            name (str): Desired symlink name (e.g., 'my_uart')
        Returns:
            bool: True if rule was set successfully, False otherwise
        """
        rule = f'SUBSYSTEM=="tty", ATTRS{{serial}}=="{serial}", SYMLINK+="{name}"'

        rules_path = '/etc/udev/rules.d/99-uart-custom-names.rules'
        try:
            # Check for root permissions
            if os.geteuid() != 0:
                raise PermissionError("Root permissions required to set udev rules.")
            # Append or update the rule
            updated = False
            if os.path.exists(rules_path):
                with open(rules_path, 'r') as f:
                    lines = f.readlines()
                for i, line in enumerate(lines):
                    if f'ATTRS{{serial}}=="{serial}"' in line:
                        lines[i] = rule
                        updated = True
                if not updated:
                    lines.append(rule)
                with open(rules_path, 'w') as f:
                    f.writelines(lines)
            else:
                with open(rules_path, 'w') as f:
                    f.write(rule)
            # Reload udev rules
            subprocess.run(['udevadm', 'control', '--reload-rules'], check=True)
            subprocess.run(['udevadm', 'trigger'], check=True)
            return True
        except Exception as e:
            print(f"Failed to set udev rule: {e}")
            return False
