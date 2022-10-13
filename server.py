from stegano import lsb


IMG_FILENAME = 'img.png'
SECRET = 'PMR3421'


def hide_secret_in_img():
    secret_img = lsb.hide(IMG_FILENAME, SECRET)
    secret_img.save(f'secret-{IMG_FILENAME}')

    revealed_secret = lsb.reveal(f'secret-{IMG_FILENAME}')

    print('A mensagem escondida é:', revealed_secret)


hide_secret_in_img()
