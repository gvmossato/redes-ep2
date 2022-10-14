import io
import socket

from stegano import lsb


HOST = '127.0.0.1'
PORT = 50007
IMG_FILENAME = 'img.png'
SECRET = 'PMR3421'


def img2bytes(image, format):
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format=format)
    return img_byte_arr.getvalue()


img_path = f"assets\\{IMG_FILENAME}"
img_format = IMG_FILENAME.split('.')[-1]

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: # IPv4 and TCP
    s.bind((HOST, PORT))
    s.listen(1)

    print(f'Servidor escutando em: {HOST}:{PORT}\n')

    while True:
        conn, addr = s.accept() # Await for connection

        print(f'Cliente conectado: {addr[0]}:{addr[1]}')

        data = img2bytes(lsb.hide(img_path, SECRET), img_format)
        conn.sendall(data)
        conn.shutdown(socket.SHUT_RDWR)
        conn.close()
