python
import socket
import logging
import argparse
import time

client_port = None
server_addr = ('127.0.0.1', client_port)

def client_handler():
    with socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) as client_socket:
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 30000)

        name = input("")
        client_seqno = 0

        # Send identification packet
        data = f's|{client_seqno}|{name}'.encode()
        client_seqno = (client_seqno + 1) % 2
        await_ack(data, client_socket, client_seqno, server_addr)
        client_seqno = (client_seqno + 1) % 2

        # Input cycle
        while True:
            message = input()
            data = f'm|{client_seqno}|{message}'.encode()
            client_seqno = (client_seqno + 1) % 2
            await_ack(data, client_socket, client_seqno, server_addr)
            client_seqno = (client_seqno + 1) % 2

if name == "main":
    parser = argparse.ArgumentParser()
    parser.add_argument
    ("client_port", type=int)
    args = parser.parse_args()

    client_port = args.client_port
    
    try:
        client_handler()
    except KeyboardInterrupt:
        logging.info("Exiting")