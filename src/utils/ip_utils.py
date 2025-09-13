import socket

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connect to an external server (e.g., Google's DNS)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
    except Exception:
        ip_address = "Unable to get local IP"
    finally:
        s.close()
    return ip_address

# Example usage
# print(f"Local IP Address: {get_local_ip()}")
