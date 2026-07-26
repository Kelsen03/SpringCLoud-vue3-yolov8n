"""SOCKS5 → HTTP Proxy Bridge — 让 Docker Desktop 走 VPN"""
import socket
import threading
import struct
import sys

HTTP_PORT = 7890
SOCKS_HOST = "127.0.0.1"
SOCKS_PORT = 1080


def socks5_connect(host, port):
    """SOCKS5 CONNECT, return socket to target via proxy"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(30)
    s.connect((SOCKS_HOST, SOCKS_PORT))
    # handshake: no auth
    s.sendall(b"\x05\x01\x00")
    if s.recv(2) != b"\x05\x00":
        raise Exception("SOCKS5 handshake failed")
    # CONNECT request — use domain name
    host_bytes = host.encode()
    req = b"\x05\x01\x00\x03" + bytes([len(host_bytes)]) + host_bytes + struct.pack("!H", port)
    s.sendall(req)
    resp = s.recv(10)
    if resp[1] != 0x00:
        raise Exception(f"SOCKS5 connect failed, code={resp[1]}")
    s.settimeout(None)
    return s


def relay(src, dst, name):
    try:
        while True:
            data = src.recv(8192)
            if not data:
                break
            dst.sendall(data)
    except Exception:
        pass
    finally:
        try:
            src.close()
        except Exception:
            pass
        try:
            dst.close()
        except Exception:
            pass


def handle(client_sock):
    try:
        data = client_sock.recv(4096)
        if not data:
            client_sock.close()
            return

        lines = data.split(b"\r\n")
        first_line = lines[0].decode()
        method, url, _ = first_line.split()

        if method == "CONNECT":
            # HTTPS tunnel
            host, port_str = url.split(":")
            port = int(port_str)
            try:
                remote = socks5_connect(host, port)
                client_sock.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")
                t1 = threading.Thread(target=relay, args=(client_sock, remote, "C→R"))
                t2 = threading.Thread(target=relay, args=(remote, client_sock, "R→C"))
                t1.daemon = True
                t2.daemon = True
                t1.start()
                t2.start()
                t1.join()
                t2.join()
            except Exception as e:
                client_sock.sendall(f"HTTP/1.1 502 Bad Gateway\r\n\r\n{str(e)}".encode())
                client_sock.close()
        else:
            # HTTP forward
            if "://" in url:
                scheme, rest = url.split("://", 1)
                if "/" in rest:
                    host_part, path = rest.split("/", 1)
                else:
                    host_part = rest
                    path = ""
            else:
                if "/" in url:
                    host_part, path = url.split("/", 1)
                else:
                    host_part = url
                    path = ""

            if ":" in host_part:
                host, port_str = host_part.rsplit(":", 1)
                port = int(port_str)
            else:
                host = host_part
                port = 80

            # rebuild request with relative path
            if path:
                new_first = f"{method} /{path} HTTP/1.1"
            else:
                new_first = f"{method} / HTTP/1.1"

            # rewrite Host header
            new_lines = [new_first]
            for line in lines[1:]:
                decoded = line.decode(errors="replace")
                if decoded.lower().startswith("host:"):
                    new_lines.append(f"Host: {host}")
                elif decoded.lower().startswith("proxy-connection:"):
                    new_lines.append(f"Connection: keep-alive")
                elif decoded.lower().startswith("connection:"):
                    continue
                else:
                    new_lines.append(decoded)
            new_req = "\r\n".join(new_lines).encode() + b"\r\n\r\n"

            try:
                remote = socks5_connect(host, port)
                remote.sendall(new_req)
                t1 = threading.Thread(target=relay, args=(remote, client_sock, "R→C"))
                t2 = threading.Thread(target=relay, args=(client_sock, remote, "C→R"))
                t1.daemon = True
                t2.daemon = True
                t1.start()
                t2.start()
                t1.join()
                t2.join()
            except Exception as e:
                err = f"HTTP/1.1 502 Bad Gateway\r\n\r\n{str(e)}"
                client_sock.sendall(err.encode())
                client_sock.close()
    except Exception:
        pass
    finally:
        try:
            client_sock.close()
        except Exception:
            pass


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("127.0.0.1", HTTP_PORT))
    server.listen(50)
    print(f"SOCKS5→HTTP bridge listening on 127.0.0.1:{HTTP_PORT}")
    print(f"Forwarding to SOCKS5 {SOCKS_HOST}:{SOCKS_PORT}")
    while True:
        client, addr = server.accept()
        t = threading.Thread(target=handle, args=(client,))
        t.daemon = True
        t.start()


if __name__ == "__main__":
    main()
