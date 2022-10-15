import io
import socket

from time import sleep
from stegano import lsb


HOST = '127.0.0.1'
PORT = 50007
SEG_SIZE = 1024


def img2bytes(image, format):
    image_byte_arr = io.BytesIO()
    image.save(image_byte_arr, format=format)
    return image_byte_arr.getvalue()

def parse_msg(byte_arr):
    client_msg = byte_arr.decode('utf-8')

    lines = client_msg.split('\n')
    image_path = lines[0].split(' ')[-1]
    secret = lines[1]
    return client_msg, image_path, secret

def gen_packets(byte_arr):
    return [byte_arr[i : i+SEG_SIZE] for i in range(0, len(byte_arr), SEG_SIZE)]

def update_num_sent(curr_num_sent, to_addr, verbose=True):
    curr_num_sent += 1
    if verbose:
        print(
            f'Sent {curr_num_sent} packets to {to_addr[0]}:{to_addr[1]}',
            end='\r'
        )
    return curr_num_sent


print(f'Server listening to {HOST}:{PORT}\n')

while True:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((HOST, PORT))

    received_data, client_addr = s.recvfrom(1024)

    client_msg, image_path, secret = parse_msg(received_data)
    print(
        f"Message received from client {client_addr[0]}:{client_addr[1]}:\n{client_msg}\n"
    )

    img_format = image_path.split('.')[-1]
    send_data = img2bytes(lsb.hide(image_path, secret), img_format)
    send_packets = gen_packets(send_data)
    num_sent = 0

    for packet in send_packets:
        s.sendto(packet, client_addr)
        num_sent = update_num_sent(num_sent, client_addr)
        sleep(1e-3) # Arbitrary amount of time: prevents server and client desync on send-receive

    s.sendto(b"EOF", client_addr) # End-Of-File bytearray finishes transmission
    num_sent = update_num_sent(num_sent, client_addr)

    s.shutdown(socket.SHUT_RDWR)
    s.close()
