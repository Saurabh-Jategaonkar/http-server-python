import socket
OK_200 = b"HTTP/1.1 200 OK\r\n\r\n"
ERR_404 = b"HTTP/1.1 404 Not Found\r\n\r\n"

def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    conn, _ = server_socket.accept()  # wait for client
    data = conn.recv(1024)
    response = parse_msg(data)
    conn.send(response)

def parse_msg(msg: bytes):
    headers = msg.split(b"\r\n")
    top_header = headers[0]
    top_header_split = top_header.split(b" ")
    path = top_header_split[1]
    content = path.decode("utf-8")
    if path == b"/":
        return OK_200
    if not content.startswith("/echo/"):
        return ERR_404
    content = content.removeprefix("/echo/")
    if content:
        resp = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(content)}\r\n\r\n{content}\r\n\r\n".encode()
        print(f"resp: {resp}")
        return resp
    else:
        return ERR_404
    
if __name__ == "__main__":
    main()