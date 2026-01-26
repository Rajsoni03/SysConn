import serial
import time
import requests
from requests.auth import HTTPDigestAuth
from abc import ABC, abstractmethod

init_command=[b"\x50", b"\x51"]

class Relay(ABC):
    """Base class for Relay"""
    @abstractmethod
    def initialize(self):
        raise NotImplementedError("This method should be overridden by subclasses")
    
    @abstractmethod
    def toggle(self, relay_no):
        raise NotImplementedError("This method should be overridden by subclasses")
    
    @abstractmethod
    def on(self, relay_no):
        """Turn on the specified relay."""
        raise NotImplementedError("This method should be overridden by subclasses")
    
    @abstractmethod
    def off(self, relay_no):
        """Turn off the specified relay."""
        raise NotImplementedError("This method should be overridden by subclasses")
    
    @abstractmethod
    def power_on_reset(self, relay_no):
        """Power on reset the specified relay."""
        raise NotImplementedError("This method should be overridden by subclasses")

class SerialRelay(Relay):
    def __init__(self, uart_port, baudrate=9600):
        """Initialize the Serial Relay with the specified UART port and baudrate."""
        self.serial = serial.Serial(uart_port, baudrate)
        self.prev_state = [0] * 8  # Assuming 8 relays
        
    def initialize(self):
        print("Relay initialization in progress. Please wait...")
        time.sleep(1)
        self.serial.write(init_command[0])
        time.sleep(1)
        self.serial.write(init_command[1])
        time.sleep(1)
        print("Relay initialization Done.")

    def toggle(self, relay_no):
        """Toggle the specified relay."""
        self.set_state(relay_no, self.prev_state[relay_no-1] ^ 1)

    def on(self, relay_no):
        """Turn on the specified relay."""
        self.set_state(relay_no, 1)

    def off(self, relay_no):
        """Turn off the specified relay."""
        self.set_state(relay_no, 0)
    
    def power_on_reset(self, relay_no):
        """Power on reset the specified relay."""
        self.set_state(relay_no, 0)
        time.sleep(1)
        self.set_state(relay_no, 1)

    # helper function to set the state of a relay
    @staticmethod
    def set_state(self, relay_no, state):
        num = (relay_no-1) ^ state
        byte_string = num.to_bytes(1, byteorder='big')
        self.serial.write(byte_string)
        self.prev_state[relay_no-1] = num


class IpRelay(Relay):
    def __init__(self, ip_address, username, password):
        """Initialize the IP Relay with the specified IP address, username, and password."""
        self.ip_address = ip_address
        self.prev_state = [False] * 8   # Assuming 8 relays
        self.base_url = f"http://{self.ip_address}/restapi"
        self.auth = auth=HTTPDigestAuth(username, password)
        self.proxies = {"http" : None, "https" : None}
        
    def initialize(self):
        print("Relay initialization in progress. Please wait...")
        self.sync_state()            
        print("Relay initialization Done.")

    def sync_state(self):
        url = self.base_url + f"/relay/outlets/all;/physical_state/"
        headers = {"Accept": "application/json"}
        
        try:
            response = requests.get(url, auth=self.auth, headers=headers, proxies=self.proxies)
            response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
            self.prev_state = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")

    def toggle(self, relay_no):
        """Toggle the specified relay."""
        return self.set_state(relay_no, self.prev_state[relay_no-1] ^ 1)

    def on(self, relay_no):
        """Turn on the specified relay."""
        return self.set_state(relay_no, 1)
    
    def off(self, relay_no):
        """Turn off the specified relay."""
        return self.set_state(relay_no, 0)
    
    def power_on_reset(self, relay_no):
        """Power on reset the specified relay."""
        self.set_state(relay_no, 0)
        time.sleep(1)
        self.set_state(relay_no, 1)
        time.sleep(1)

    # helper function to toggle the state of a relay
    @staticmethod
    def set_state(self, relay_no, state):
        url = self.base_url + f"/relay/outlets/{relay_no - 1}/state/"
        data = {"value": "true" if state == 1 else "false"}
        headers = {"X-CSRF": "x"}
        
        try:
            response = requests.put(url, auth=self.auth, headers=headers, data=data, proxies=self.proxies)
            response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        except Exception as e:
            print(f"Request failed: {e}")
            
        self.sync_state()
        return response.status_code == 204


class RelayFactory:
    @staticmethod
    def create_relay(relay_type, *args, **kwargs):
        if relay_type == "serial":
            return SerialRelay(*args, **kwargs)
        elif relay_type == "ip":
            return IpRelay(*args, **kwargs)
        else:
            raise ValueError("Unknown relay type")


if __name__ == "__main__":
    relay = RelayFactory.create_relay("ip", "<ip_address>", "admin", "1234")
    relay.initialize()

    for i in range(1, 9):
        relay.on(i)
        time.sleep(2)
        relay.off(i)
        time.sleep(2)
