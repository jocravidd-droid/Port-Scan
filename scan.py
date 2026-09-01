import asyncio

print(r"""
╭───────────────────────────────────────────────╮
│    ___  ___  ___ _____ ___  ___   _   _  _    │
│   | _ \/ _ \| _ \_   _/ __|/ __| /_\ | \| |   │
│   |  _/ (_) |   / | | \__ \ (__ / _ \| .` |   │
│   |_|  \___/|_|_\ |_| |___/\___/_/ \_\_|\_|   │
│                                               │
│   asynchronous tcp scanner  //  python 3      │
╰───────────────────────────────────────────────╯""")


class Scanner:
    def __init__(self, target, port_range, timeout_value, semaphore):
        self.target = target
        self.port_range = port_range
        self.results = []
        self.timeout_value = timeout_value
        self.semaphore = semaphore
    async def scan(self):
        tasks = [scan_port(self.target, port, self.timeout_value, self.semaphore) for port in self.port_range]
        result = await asyncio.gather(*tasks)
        save = [p for p in result if p is not None]
        return save

async def scan_port(target, port, timeout_value, semaphore):
    async with semaphore:
        try:
            conn = asyncio.open_connection(target, port)
            _reader, writer = await asyncio.wait_for(conn, timeout=timeout_value)
            writer.close()
            await writer.wait_closed()
            return port
        except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
            return None

try:
    target = input('\nTarget: ')
    start_port = int(input("Start_port: "))
    end_port = int(input('End_port (limit 65535): '))
    timeout_value = int(input('Timeout: '))
    semaphore = asyncio.Semaphore(int(input('Max Connections: ')))
    if start_port > end_port:
        print(f"\nStart port ({start_port}) must be smaller than end port ({end_port})")
    elif start_port < 1:
        print("Start port must be at least 1")
    elif end_port > 65535:
        print("End port cannot exceed 65535")
    else:
        sc = Scanner(target, range(start_port, end_port + 1), timeout_value, semaphore)
        info = asyncio.run(sc.scan())
        print(f'\nPort Found for {target}: {info}')
except ValueError:
    print('\nEnter an integer')
except (EOFError, KeyboardInterrupt):
    print('\nInterruption Forcé')