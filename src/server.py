import io
import socket

from time import sleep
from stegano import lsb


HOST = '127.0.0.1'
PORT = 50007
SEG_SIZE = 1024


def img2bytes(image, format):
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format=format)
    return img_byte_arr.getvalue()

def parse_msg(byte_arr):
    client_msg = byte_arr.decode('utf-8')

    lines = client_msg.split('\n')
    image_path = lines[0].split(' ')[-1]
    secret = lines[1]
    return client_msg, image_path, secret

def bytes_split(byte_arr):
    return [byte_arr[i : i+SEG_SIZE] for i in range(0, len(byte_arr), SEG_SIZE)]


print(f'Server listening to {HOST}:{PORT}\n')

while True:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((HOST, PORT))

    received_data, addr = s.recvfrom(1024)

    client_msg, image_path, secret = parse_msg(received_data)
    print(f"Message received from client {addr[0]}:{addr[1]}:\n{client_msg}\n")

    img_format = image_path.split('.')[-1]
    send_data = img2bytes(lsb.hide(image_path, secret), img_format)
    send_packets = bytes_split(send_data)
    num_sent = 0

    for packet in send_packets:
        s.sendto(packet, addr)
        num_sent += 1
        print(f'Sent {num_sent} packets to {addr[0]}:{addr[1]}', end='\r')
        sleep(1e-3) # Arbitrary amount of time to prevent server-client send-receive desync

    s.sendto(b"EOF", addr) # End-Of-File bytearray finishes transmission
    num_sent += 1
    print(f'Sent {num_sent} packets to {addr[0]}:{addr[1]}', end='\r')

    s.shutdown(socket.SHUT_RDWR)
    s.close()
