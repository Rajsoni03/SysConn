import os
import subprocess
from dataclasses import dataclass
from typing import List, Optional

import pyudev


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


if __name__ == "__main__":
    manager = UARTUdevManager()
    devices = manager.list_uart_devices()

    print("\nDetected UART devices:\n")
    for idx, d in enumerate(devices):
        print(f"[{idx}] {d.devnode}")
        print(f"    Serial       : {d.serial}")
        print(f"    Vendor ID    : {d.vendor_id}")
        print(f"    Product ID   : {d.product_id}")
        print(f"    Manufacturer : {d.manufacturer}")
        print(f"    Product      : {d.product}\n")

    # Example: auto-create rules
    # rules = []
    # for d in devices:
    #     if not d.serial:
    #         continue

    #     symlink = f"uart_{d.serial}"
    #     rules.append(
    #         manager.generate_udev_rule(
    #             serial=d.serial,
    #             symlink_name=symlink,
    #             vendor_id=d.vendor_id,
    #             product_id=d.product_id,
    #         )
    #     )

    # if rules:
    #     print("Generated udev rules:\n")
    #     for r in rules:
    #         print(r)
