import os
import sys
import threading
import socket
from typing import Optional
import argparse

HOST = "localhost"
PORT = 4221
VERSION = b"HTTP/1.1"
OK_MESSAGE = b"OK"
OK_STATUS_CODE = b"200"
NOT_FOUND_MESSAGE = b"Not Found"
1
NOT_FOUND_STATUS_CODE = b"404"
def process_request(conn: socket.socket, addr: str, args: argparse.Namespace) -> None:
    data = conn.recv(1024)
    data_str = data.decode("utf-8")
    lines = data_str.split("\r\n")
    assert len(lines) > 0
    start_line = lines[0]
    parts = start_line.split(" ")
    assert len(parts) == 3
    method = parts[0]
    path = parts[1]
    version = parts[2]
    assert method == "GET"
    assert version == "HTTP/1.1"
    path_components = [c for c in path.split("/") if c]
    request_headers = []
    for line in lines[1:]:
        if not line:
            break
        header_parts = line.split(": ")
        assert len(header_parts) == 2
        header_type = header_parts[0]
        header_content = header_parts[1]
        request_headers.append((header_type, header_content))
    response_headers = []
    response_body: Optional[str] = None
    if len(path_components) == 0:
        req_status_code = OK_STATUS_CODE
        req_message = OK_MESSAGE
    elif path_components[0] == "echo":
        req_status_code = OK_STATUS_CODE
        req_message = OK_MESSAGE
        path_suffix = "/".join(path_components[1:])
        response_headers = [
            "Content-Type: text/plain",
            f"Content-Length: {len(path_suffix)}",
        ]
        response_body = path_suffix
    elif path_components[0] == "user-agent":
        req_status_code = OK_STATUS_CODE
        req_message = OK_MESSAGE
        user_agent = None
        for header in request_headers:
            if header[0] == "User-Agent":
                user_agent = header[1]
                break
        if user_agent:
            response_headers = [
                "Content-Type: text/plain",
                f"Content-Length: {len(user_agent)}",
            ]
            response_body = user_agent
        else:
            req_status_code = NOT_FOUND_STATUS_CODE
            req_message = NOT_FOUND_MESSAGE
    elif path_components[0] == "files":
        assert args.directory is not None
        files = [
            f
            for f in os.listdir(args.directory)
            if os.path.isfile(os.path.join(args.directory, f))
        ]
        expected_file = path_components[1]
        if expected_file in files:
            req_status_code = OK_STATUS_CODE
            req_message = OK_MESSAGE
            with open(os.path.join(args.directory, expected_file), "r") as f:
                response_body = f.read()
            response_headers = [
                "Content-Type: application/octet-stream",
                f"Content-Length: {len(response_body)}",
            ]
        else:
            req_status_code = NOT_FOUND_STATUS_CODE
            req_message = NOT_FOUND_MESSAGE
    else:
        req_status_code = NOT_FOUND_STATUS_CODE
        req_message = NOT_FOUND_MESSAGE
    response = b"%s %s %s\r\n" % (VERSION, req_status_code, req_message)
    for header in response_headers:
        response += header.encode("utf-8") + b"\r\n"
    if response_body:
        response += b"\r\n" + response_body.encode("utf-8")
    response += b"\r\n"
    conn.send(response)
    conn.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", default=None, required=False, type=str)
    args = parser.parse_args()
    server_socket = socket.create_server((HOST, PORT), reuse_port=True)
    running = True
    thread_pool = []
    while running:
        conn, addr = server_socket.accept()
        t = threading.Thread(target=process_request, args=(conn, addr, args))
        thread_pool.append(t)
        t.start()
    print("Shutting down server...")
    server_socket.close()
    for t in thread_pool:
        t.join()
if __name__ == "__main__":
    main()
    sys.exit(main())