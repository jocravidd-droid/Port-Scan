import asyncio

class Scanner:
    def __init__(self, target, port_range):
        self.target = target
        self.port_range = port_range
        self.results = []
    async def scan(self):
        tasks = [scan_port(self.target, port) for port in self.port_range]
        result = await asyncio.gather(*tasks)
        save = [p for p in result if p is not None]
        return save

async def scan_port(target, port):
    try:
        conn = asyncio.open_connection(target, port)
        reader, writer = await asyncio.wait_for(conn, timeout=1)
        writer.close()
        return port
    except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
        return None


try:
    target = input('Target: ')
    max_port = int(input('MAX PORT: '))
    sc = Scanner(target, range(1, max_port + 1))
    info = asyncio.run(sc.scan())
    print(info)
except ValueError:
    print('\nEnter an integer')
