import asyncio
from ipaddress import IPv6Address
import socket


async def is_socket_open(ip: IPv6Address, port: int | str):
    """Check if a socket is open asynchronously."""
    conn = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    conn.setblocking(False)
    try:
        ip_str = str(ip)
        await asyncio.get_event_loop().sock_connect(conn, (ip_str, int(port)))
        conn.shutdown(socket.SHUT_RDWR)
        return True
    except (OSError, asyncio.CancelledError):
        return False
    finally:
        conn.close()
