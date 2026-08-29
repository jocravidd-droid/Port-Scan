import socket

class Scanner:
    def __init__(self, target, port_range):
        self.target = target
        self.port_range = port_range
        self.results = []

    def scan(self):
        for port in self.port_range:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex((self.target, port))
                if result == 0:
                    self.results.append(port)
        return self.results

mon_scan = Scanner(input("IP OR DOMAINE: "), range(1, 100))
print(mon_scan.scan())