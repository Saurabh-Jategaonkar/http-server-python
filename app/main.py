# Uncomment this to pass the first stage
import socket
def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")
    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    client_socket, address = server_socket.accept()  # wait for client
    data = client_socket.recv(1024)
    response = "HTTP/1.1 200\r\n\r\n"
    lines = data.decode().split("\r\n")
    verb, path, version = lines[0].split(" ")
    if path == "/":
        response = "HTTP/1.1 200\r\n\r\n"
    else:
        response = "HTTP/1.1 404\r\n\r\n"
    client_socket.send(response.encode())
if __name__ == "__main__":
    main()