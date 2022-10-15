import argparse
import socket
import io

from stegano import lsb


HOST = '127.0.0.1'
PORT = 50007
SEG_SIZE = 1024
INT_SIZE = 2


def get_cmd_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s",
        "--secret",
        type=str,
        required=True,
        help="secret message to hide"
    )
    parser.add_argument(
        "-i",
        "--image",
        type=str,
        required=True,
        help="path to image that will hide the secret"
    )
    return parser.parse_args()

def byte2int(data):
    return int.from_bytes(data, 'big')


output_path = './assets/secret-img.png'
cmd_args = get_cmd_args()
send_msg_data = str.encode(f"STEGANO {cmd_args.image}\n{cmd_args.secret}")


s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.sendto(send_msg_data, (HOST, PORT))

buffer_size_data, server_addr = s.recvfrom(INT_SIZE) # 2 bytes for interger
buffer_size = byte2int(buffer_size_data)
buffer = bytearray(buffer_size*SEG_SIZE)

for i in range(buffer_size):
    received_pack, server_addr = s.recvfrom(INT_SIZE+SEG_SIZE) # Accounts for sequence number + image data packet
    received_sequence_num_data = received_pack[:INT_SIZE]
    received_image_data = received_pack[INT_SIZE:]

    integer_rec = byte2int(received_sequence_num_data)


    buffer[integer_rec*SEG_SIZE:integer_rec*SEG_SIZE+SEG_SIZE] = received_image_data

    print(
        f'Received {i+1}/{buffer_size} packets from {server_addr[0]}:{server_addr[1]}',
        end='\r'
    )

with io.open(output_path, "wb") as steganography:
    steganography.write(buffer)

s.shutdown(socket.SHUT_RDWR)
s.close()

print('\n\nRevealed secret:', lsb.reveal(output_path))
