import sys, os, socket, threading, re

def http_response(conn, addr, directory=None):
    data: bytes = conn.recv(1024).decode()
    lines = data.split("\r\n")
    method = lines[0].split(" ")[0]
    path = lines[0].split(" ")[1]
    echo_keyword = path.split("/")[1]

    body = lines[-1]
    if path == "/":
        conn.send(b"HTTP/1.1 200 OK\r\n\r\n")
    elif echo_keyword == "echo":
        pattern = r"/echo/(.*)"
        match = re.search(pattern, path)
        response_body = ""
        if match:
            response_body = match.group(1)
        response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(response_body)}\r\n\r\n{response_body}"
        conn.send(response.encode())
    elif echo_keyword == "user-agent":
        user_agent = lines[2].split(" ")[1]
        response_body = user_agent
        response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(response_body)}\r\n\r\n{response_body}"
        conn.send(response.encode())
    elif echo_keyword == "files":
        pattern = r"/files/(.*)"
        match = re.search(pattern, path)
        filename = ""
        if match:
            filename = match.group(1)
        data = "no file"
        if method == "POST":
            filepath = os.path.join(directory, filename)
            file_object = open(filepath, "w")
            file_object.write(body)
            file_object.close()
            data = "file created"
            response = "HTTP/1.1 201 Created\r\n"
            response += "Content-Type: text/plain\r\n"
            response += f"Content-Length: {len(data)}\r\n\r\n"
            response += data

            conn.send(response.encode())
        else:
            if filename in os.listdir(directory):
                filepath = os.path.join(directory, filename)
                file_object = open(filepath)
                data = file_object.read()
                file_object.close()
                response = "HTTP/1.1 200 OK\r\n"
                response += "Content-Type: application/octet-stream\r\n"
                response += f"Content-Length: {len(data)}\r\n\r\n"
                response += data
            else:
                response = "HTTP/1.1 404 Not Found\r\n"
                response += "Content-Type: text/plain\r\n"
                response += f"Content-Length: {len(data)}\r\n\r\n"
                response += data
            conn.send(response.encode())
    else:
        conn.send(b"HTTP/1.1 404 Not Found\r\n\r\n")
    conn.close()

def main(directory=None):
    print("Logs from your program will appear here!")
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Received a connection from {client_address}")
        threading.Thread(
            target=http_response, args=[client_socket, client_address, directory]
        ).start()

if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--directory":
        directory = sys.argv[2]
        main(directory)
    else:
        main()
