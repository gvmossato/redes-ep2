import io
import socket

from stegano import lsb


HOST = '127.0.0.1'
PORT = 50007


def img2bytes(image, format):
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format=format)
    return img_byte_arr.getvalue()

def parse_msg(byte_str):
    client_msg = byte_str.decode('utf-8')

    lines = client_msg.split('\n')
    image_path = lines[0].split(' ')[-1]
    secret = lines[1]
    return client_msg, image_path, secret


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(1)

    print(f'Server listening to {HOST}:{PORT}\n')

    while True:
        conn, addr = s.accept()

        with conn:
            received_data = conn.recv(1024)

            client_msg, image_path, secret = parse_msg(received_data)
            print(
                f"Message received from client {addr[0]}:{addr[1]}:\n{client_msg}\n")

            img_format = image_path.split('.')[-1]
            send_data = img2bytes(lsb.hide(image_path, secret), img_format)

            conn.sendall(send_data)
            conn.shutdown(socket.SHUT_RDWR)
            conn.close()
