import argparse
import socket
import io

from stegano import lsb


HOST = '127.0.0.1'
PORT = 50007


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


output_path = './assets/secret-img.png'
cmd_args = get_cmd_args()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

    send_data = str.encode(f"STEGANO {cmd_args.image}\n{cmd_args.secret}")
    s.send(send_data)

    received_data = s.recv(int(1e7)) # Images up to 10 MB

    with io.open(output_path, "wb") as steganography:
        steganography.write(received_data)

    s.shutdown(socket.SHUT_RDWR)
    s.close()

print('Revealed secret:', lsb.reveal(output_path))
