# ======== #
# Packages #
# ======== #

import argparse
import socket
import io

from stegano import lsb

# ======= #
# Globals #
# ======= #

HOST = '127.0.0.1'
PORT = 50007

SEG_SIZE = 1024
INT_SIZE = 2

# ========= #
# Functions #
# ========= #

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

def bytes2int(data):
    return int.from_bytes(data, 'big')

# ====== #
# Script #
# ====== #

output_path = './assets/secret-img.png'
cmd_args = get_cmd_args()
send_msg_bytes = str.encode(f"STEGANO {cmd_args.image}\n{cmd_args.secret}")

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.sendto(send_msg_bytes, (HOST, PORT))

num_segs_bytes, server_addr = s.recvfrom(INT_SIZE)
num_segs = bytes2int(num_segs_bytes)
buffer = bytearray(num_segs * SEG_SIZE)

for i in range(num_segs):
    recv_seg, server_addr = s.recvfrom(INT_SIZE + SEG_SIZE) # Sequence number + Image data
    seq_num = bytes2int(recv_seg[:INT_SIZE])
    image_bytes = recv_seg[INT_SIZE:]

    buffer_start_pos = seq_num * SEG_SIZE
    buffer[buffer_start_pos : buffer_start_pos+SEG_SIZE] = image_bytes

    print(
        f'Received {i+1}/{num_segs} packets from {server_addr[0]}:{server_addr[1]}',
        end='\r'
    )

with io.open(output_path, "wb") as steganography:
    steganography.write(buffer)

s.shutdown(socket.SHUT_RDWR)
s.close()

print('\n\nRevealed secret:', lsb.reveal(output_path))
