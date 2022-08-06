import cv2
from socket_classes import socket_classes

# Создаётся сокет отправления
sender = socket_classes.ImageSender(
    connect_to="tcp://{}:{}".format(
        '127.0.0.1',
        '5555'
    )
)
print('Connect the ImageSender object to {}:{}'.format(
    '127.0.0.1',
    '5555')
)

# Создаётся объект считывания видео из файла
video_stream = cv2.VideoCapture('video.mp4')

print('Streaming frames to the server...')
while video_stream.isOpened():
    # читает какждый кадр и отправляет картинку на сервер
    try:
        ret, frame = video_stream.read()
        if ret:
            rep, jpg_buffer = cv2.imencode(".jpg", frame)
            sender.send_jpg('host', jpg_buffer)
    except Exception as err:
        sender.reset_socket()
        print(err)
