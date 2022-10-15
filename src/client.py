import argparse
import socket
import io

from stegano import lsb


HOST = '127.0.0.1'
PORT = 50007
SEG_SIZE = 1024


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

def update_num_received(curr_num_received, from_addr, verbose=True):
    curr_num_received += 1
    if verbose:
        print(
            f'Received {curr_num_received} packets from {from_addr[0]}:{from_addr[1]}',
            end='\r'
        )
    return curr_num_received


output_path = './assets/secret-img.png'
cmd_args = get_cmd_args()
send_data = str.encode(f"STEGANO {cmd_args.image}\n{cmd_args.secret}")

buffer = bytearray()
received_pack = None
num_received = 0

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.sendto(send_data, (HOST, PORT))

while received_pack != b"EOF":
    received_pack, server_addr = s.recvfrom(SEG_SIZE)
    buffer.extend(received_pack)
    num_received = update_num_received(num_received, server_addr)

with io.open(output_path, "wb") as steganography:
    steganography.write(buffer)

s.shutdown(socket.SHUT_RDWR)
s.close()

print('\n\nRevealed secret:', lsb.reveal(output_path))
