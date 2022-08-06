import cv2
from socket_classes import socket_classes
from imutils.video import WebcamVideoStream

# initialize the ImageSender object with the socket address of the server
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

# initialize the video stream
video_stream = WebcamVideoStream(src=0)

video_stream.start()
# a camera warmup time of 2.0 seconds

frame = video_stream.read()

print('Video Size is', frame.shape)
print('Streaming frames to the server...')
while True:
    # read the frame from the camera and send it to the server
    try:
        frame = video_stream.read()

        rep, jpg_buffer = cv2.imencode(".jpg", frame)
        if rep:
            sender.send_jpg('host', jpg_buffer)
    except Exception as err:
        sender.reset_socket()
