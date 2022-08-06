import cv2
from socket_classes import socket_classes
from imutils.video import WebcamVideoStream

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

# Создаётся объект записи видео с вебкамеры
video_stream = WebcamVideoStream(src=0)

video_stream.start()
# камера включается около 2 секунд
print('Streaming frames to the server...')
while True:
    # читает какждый кадр и отправляет картинку на сервер
    try:
        frame = video_stream.read()

        rep, jpg_buffer = cv2.imencode(".jpg", frame)
        if rep:
            sender.send_jpg('host', jpg_buffer)
    except Exception as err:
        sender.reset_socket()
        if video_stream.read() is None:
            video_stream = WebcamVideoStream(src=0)
            video_stream.start()
