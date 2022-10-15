import io
import socket

from time import sleep
from stegano import lsb


HOST = '127.0.0.1'
PORT = 50007
SEG_SIZE = 1024
INT_SIZE = 2


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

def count_packets(byte_arr):
    return (len(byte_arr) + SEG_SIZE - 1) // SEG_SIZE


print(f'Server listening to {HOST}:{PORT}\n')

while True:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((HOST, PORT))

    received_data, client_addr = s.recvfrom(SEG_SIZE)

    client_msg, image_path, secret = parse_msg(received_data)
    print(
        f"Message received from client {client_addr[0]}:{client_addr[1]}:\n{client_msg}\n"
    )

    img_format = image_path.split('.')[-1]
    send_data = img2bytes(lsb.hide(image_path, secret), img_format)

    num_packets = count_packets(send_data)
    send_packets = gen_packets(send_data)

    s.sendto(num_packets.to_bytes(INT_SIZE, 'big'), client_addr)

    for i in range(num_packets):
        send_packet = i.to_bytes(INT_SIZE, 'big') + send_packets[i]
        s.sendto(send_packet, client_addr)
        print(f'Sent {i+1}/{num_packets} packets to {client_addr[0]}:{client_addr[1]}', end='\r')
        sleep(1e-3) # Arbitrary amount of time: prevents server and client desync on send-receive

    s.shutdown(socket.SHUT_RDWR)
    s.close()
