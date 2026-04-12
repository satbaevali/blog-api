import sys
import socket

host = sys.argv[1] if len(sys.argv) > 1 else "redis"
port = int(sys.argv[2]) if len(sys.argv) > 2 else 6379

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    result = s.connect_ex((host, port))
    s.close()
    sys.exit(result)
except Exception:
    sys.exit(1)