import cv2
import numpy as np
from socket_classes import socket_classes

server_port = '5555'
open_port = 'tcp://*:{}'.format(server_port)
image_hub = socket_classes.ImageHub(open_port=open_port)

print('Open Port is {}'.format(open_port))
print('Receiving frames...')

hosts = {}
while True:
    try:
        host_name, jpg_buffer = image_hub.recv_jpg()

        image = np.frombuffer(jpg_buffer, dtype='uint8')
        image = cv2.imdecode(image, -1)
        width, height, channel = image.shape

        if host_name not in hosts:
            hosts[host_name] = True
            print('Producer connected >>', host_name + ':', width, height, channel)

        cv2.imshow(host_name, image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            image_hub.exit()
            break
        image_hub.send_reply(b'OK')

    except Exception as err:
        print(err)
