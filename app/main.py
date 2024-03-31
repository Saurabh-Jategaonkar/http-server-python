import socket

OK_200 = "HTTP/1.1 200 OK\r\n"
ERR_404 = "HTTP/1.1 404 Not Found\r\n"

def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    conn, _ = server_socket.accept()  # wait for client
    data = conn.recv(1024)
    response = parse_msg(data)
    print(f"response: {response}")
    conn.send(response)

def parse_msg(msg: bytes):
    headers = msg.split(b"\r\n")
    top_header = headers[0]
    top_header_split = top_header.split(b" ")
    path = top_header_split[1]
    print(path)
    content = path.decode("utf-8")
    print(content)
    if path == b"/":
        return f"{OK_200}\r\n".encode()
    elif content.startswith("/echo/"):
        content = content.removeprefix("/echo/")
        resp = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(content)}\r\n\r\n{content}\r\n\r\n".encode()
        print(f"resp: {resp}")
        return resp
    elif content.startswith("/user-agent"):
        agent_header = [
            h.decode("utf-8")
            for h in headers
            if h.decode("utf-8").startswith("User-Agent")
        ][0]
        agent = agent_header.replace("User-Agent: ", "")
        return response_template(status=OK_200, type="text/plain", content=agent)
    else:
        return f"{ERR_404}\r\n".encode()
    
def response_template(status: str, type: str, content: str):
    return f"{status}Content-Type: {type}\r\nContent-Length: {len(content)}\r\n\r\n{content}\r\n\r\n".encode()

if __name__ == "__main__":
    main()