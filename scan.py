import asyncio
from pathlib import Path
import logging

print(r"""
                ╭───────────────────────────────────────────────╮
                │    ___  ___  ___ _____ ___  ___   _   _  _    │
                │   | _ \/ _ \| _ \_   _/ __|/ __| /_\ | \| |   │
                │   |  _/ (_) |   / | | \__ \ (__ / _ \| .` |   │
                │   |_|  \___/|_|_\ |_| |___/\___/_/ \_\_|\_|   │
                │                                               │
                │   asynchronous tcp scanner  //  python 3      │
                ╰───────────────────────────────────────────────╯""")

log_dir=Path("scan")
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(

    level=logging.INFO, # logging.DEBUG, logging.WARNING, logging.ERROR, logging.CRITICAL
    format="%(asctime)s [%(levelname)s] %(message)s",
    filename=log_dir / "scan.log"

)


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
            logging.debug(f"Testing port {port}")
            conn = asyncio.open_connection(target, port)
            _reader, writer = await asyncio.wait_for(conn, timeout=timeout_value)
            writer.close()
            await writer.wait_closed()
            return port
        except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
            logging.debug(f"Port {port} closed or unreachable")
            return None
if __name__ == '__main__':
    while True:
        try:
            target = input('\nTarget or exit: ')
            if target.lower() == 'exit':
                print("\nExiting")
                break
            start_port = int(input("Start_port: "))
            end_port = int(input('End_port (limit 65535): '))
            timeout_value = int(input('Timeout: '))
            if timeout_value > 1:
                logging.warning(f"High timeout value ({timeout_value}s), scan may be slow")
            max_co = int(input('Max Connections: '))
            if max_co < end_port:
                logging.warning(f"Max connections ({max_co}) lower than port range, scan may be slow")
            semaphore = asyncio.Semaphore(max_co)
            if start_port > end_port:
                logging.error(f"Invalid range: start port {start_port} is greater than end port {end_port}")
                print(f"\nStart port ({start_port}) must be smaller than end port ({end_port})")
            elif start_port < 1:
                logging.error(f"Invalid start port: {start_port} (must be at least 1)")
                print("Start port must be at least 1")
            elif end_port > 65535:
                logging.error(f"Invalid end port: {end_port} (maximum is 65535)")
                print("End port cannot exceed 65535")
            else:
                logging.info(f"[Target: {target} - Range Port: {start_port} to {end_port} - Timeout: {timeout_value} - Max Connection: {max_co}]")
                sc = Scanner(target, range(start_port, end_port + 1), timeout_value, semaphore)
                info = asyncio.run(sc.scan())
                logging.info(f"Scan finished, {len(info)} open port(s) found: {info}")
                print(f'\nPort Found for {target}: {info}')
        except ValueError:
            print('\nEnter an integer')
        except (EOFError, KeyboardInterrupt):
            print('\n\nInterrupted')
            break