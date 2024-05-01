python
import socket
import logging
import time
from threading import Thread

SLEEP_INTERVAL = 3

server_port = None
status = True

expected_server_seqno = None
user_name = None

logging.basicConfig(filename="messenger.log", filemode='a', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

PACKET_TYPES = {
    'START': 'start',
    'MESSAGE': 'text',
    'ACK': 'ack'
}

def await_ack(packet, client_socket, expected_seqno, addr):
    client_socket.settimeout(1)

    while True:
        try:
            client_socket.sendto(packet, addr)
        
            reply, _ = client_socket.recvfrom(1024)
            reply = reply.decode()
            if reply.startswith('a|') and int(reply.split('|')[1]) == expected_seqno:
                break
        except socket.timeout:
            time.sleep(SLEEP_INTERVAL)

def handle_received_data(server_socket, data, addr):
    packet_type, seqno, payload = data.decode().split('|')
    seqno = int(seqno)

    if packet_type == PACKET_TYPES['START']:
        handle_start_packet(server_socket, seqno, payload, addr)
    elif packet_type == PACKET_TYPES['MESSAGE']:
        handle_message_packet(server_socket, seqno, payload, addr)

def handle_start_packet(server_socket, seqno, payload, addr):
    user_name = payload
    expected_server_seqno = seqno
    ack_seqno = (expected_server_seqno + 1) % 2
    data = f'{PACKET_TYPES["ACK"]}|{ack_seqno}'.encode()
    expected_server_seqno = (expected_server_seqno + 2) % 2
    server_socket.sendto(data, addr)
    logging.info(f'Start packet received from {addr} for user {user_name}')

def handle_message_packet(server_socket, seqno, payload, addr):
    print(f'{user_name}: {payload}')
    
    # Echo back the received message to the client for verification
    ack_seqno = (seqno + 1) % 2
    data = f'{PACKET_TYPES["MESSAGE"]}|{ack_seqno}|{payload}'.encode()
    server_socket.sendto(data, addr)
    logging.info(f'Message echoed back to {addr}: {payload}')

def server_thread_handler():
    global server_port
    global status

    user_name = None
    expected_server_seqno = None

    with socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) as server_socket:
        server_socket.settimeout(2)
        server_socket.bind(("0.0.0.0", server_port))
        logging.info(f'Server started on port {server_port}')
        
        while status:
            try:
                data, addr = server_socket.recvfrom(1024)
                handle_received_data(server_socket, data, addr)
            except socket.timeout:
                continue

if name == "main":
    parser = argparse.ArgumentParser()
    parser.add_argument("server_port", type=int)
    args = parser.parse_args()

    server_port = args.server_port
    
    server_thread = Thread(target=server_thread_handler)
    server_thread.start()