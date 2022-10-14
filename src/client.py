import socket
import io

from stegano import lsb


HOST = '127.0.0.1'
PORT = 50007


output_path = "assets\\secret-img.png"

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: # IPv4 and TCP
    s.connect((HOST, PORT))
    data = s.recv(int(1e7)) # Images up to 10 MB

    with io.open(output_path, "wb") as download_img:
        download_img.write(data)

print('Segredo revelado:', lsb.reveal(output_path))
