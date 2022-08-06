import zmq
import numpy as np


class ImageSender:
    """
    Запускает REQ сокет и отправляет картинки
    Arguments:
        connect_to: tcp адрес:порт узла.
    """

    def __init__(self, connect_to='tcp://127.0.0.1:5555'):
        """
        Создаёт сокет на открытом порте компьютера, 
        к которому присоединяется для того чтобы стримить
        Создаётся контекст, из контекста REQ-сокет, устанавливается опция таймаута
        чтобы имелась возможность переподключения
        """
        self.connect_to = connect_to
        self.context = SerializingContext()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.setsockopt(zmq.RCVTIMEO, 500)
        self.socket.connect(self.connect_to)

    def reset_socket(self):
        """
        Функция ресета сокета для переподключения
        """
        self.socket.close()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.setsockopt(zmq.RCVTIMEO, 500)  # milliseconds
        self.socket.connect(self.connect_to)

    def exit(self):
        """
        Выход - полноценно закрывает сокет
        """
        self.socket.setsockopt(zmq.LINGER, 0)
        self.socket.close()
        self.context.term()

    def send_image(self, msg, image):
        """
        Отправляет картинки
        Arguments:
          msg: текст сообщения или название картинки.
          image: картинка.
        Returns:
          Ответ от узла
        """
        if image.flags['C_CONTIGUOUS']:
            # если картинка уже в памяти, то оправляем
            self.socket.send_array(image, msg, copy=False)
        else:
            # если нет, то сначала добавляем в память
            image = np.ascontiguousarray(image)
            self.socket.send_array(image, msg, copy=False)
        hub_reply = self.socket.recv()  # получаем ответ
        return hub_reply

    def send_jpg(self, msg, jpg_buffer):
        """
        Отправка сообщения и jpg буфера в узел
        Arguments:
          msg: текст сообщения или название картинки
          jpg_buffer: bytestring jpg картинки
        Returns:
          Ответ от узла
        """

        self.socket.send_jpg(msg, jpg_buffer, copy=False)
        hub_reply = self.socket.recv()  # receive the reply message
        return hub_reply


class ImageHub:
    """
    Запускает REP сокет и получает картинки
    Аргументы:
        open_port: socket (порт) для получения REQ запросов
    """

    def __init__(self, open_port='tcp://*:5555'):
        """
        Создаёт socket и получает картинки
        """

        self.context = SerializingContext()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(open_port)

    def recv_image(self, copy=False):
        """
        Получает картинки и текст сообщения
        Arguments:
          copy: (опциональный) zmq copy flag.
        Returns:
          msg: текст сообщения или название картинки
          image: картинка.
        """

        msg, image = self.socket.recv_array(copy=False)
        return msg, image

    def recv_jpg(self, copy=False):
        """
        Получает текст сообщения или jpg буфер
        Arguments:
          copy: (опциональный) zmq copy flag
        Returns:
          msg: текст сообщения или название картинки
          jpg_buffer: bytestring jpg картинка
        """

        msg, jpg_buffer = self.socket.recv_jpg(copy=False)
        return msg, jpg_buffer

    def send_reply(self, reply_message=b'OK'):
        """
        Отправляет REP ответ
        Arguments:
          reply_message: ответ (bytestring 'OK')
        """
        self.socket.send(reply_message)

    def exit(self):
        self.socket.setsockopt(zmq.LINGER, 0)
        self.socket.close()
        self.context.term()


class SerializingSocket(zmq.Socket):
    """
    Нужен для отправления картинок через Numpy массивы
    """

    def send_array(self, A, msg='NoName', flags=0, copy=True, track=False):
        """
        Отправляет numpy массив с данными
        Arguments:
          A: numpy массив или картинка.
          msg: (опциональный) имя массива, имя картинки или текст сообщения.
          flags: (опциональный) zmq flags.
          copy: (опциональный) zmq copy flag.
          track: (опциональный) zmq track flag.
        """

        md = dict(
            msg=msg,
            dtype=str(A.dtype),
            shape=A.shape,
        )
        self.send_json(md, flags | zmq.SNDMORE)
        return self.send(A, flags, copy=copy, track=track)

    def send_jpg(self,
                 msg='NoName',
                 jpg_buffer=b'00',
                 flags=0,
                 copy=True,
                 track=False):
        """
        Отправляет bytestring jpg буфер
        Arguments:
          msg: имя картинки или текст сообщения.
          jpg_buffer: jpg buffer картинки.
          flags: (опциональный) zmq flags.
          copy: (опциональный) zmq copy flag.
          track: (опциональный) zmq track flag.
        """

        md = dict(msg=msg, )
        self.send_json(md, flags | zmq.SNDMORE)
        return self.send(jpg_buffer, flags, copy=copy, track=track)

    def recv_array(self, flags=0, copy=True, track=False):
        """
        Получет numpy массив с данными
        Arguments:
          flags: (опциональный) zmq flags.
          copy: (опциональный) zmq copy flag.
          track: (опциональный) zmq track flag.
        Returns:
          msg: имя картинки или текст сообщения.
          A: numpy массив или раскодированная картинка.
        """

        md = self.recv_json(flags=flags)
        msg = self.recv(flags=flags, copy=copy, track=track)
        A = np.frombuffer(msg, dtype=md['dtype'])
        return md['msg'], A.reshape(md['shape'])

    def recv_jpg(self, flags=0, copy=True, track=False):
        """
        Получет numpy массив с данными
        Arguments:
          flags: (опциональный) zmq flags.
          copy: (опциональный) zmq copy flag.
          track: (опциональный) zmq track flag.
        Returns:
          msg: имя картинки или текст сообщения.
          jpg_buffer: bytestring jpg картинки.
        """

        md = self.recv_json(flags=flags)  # metadata text
        jpg_buffer = self.recv(flags=flags, copy=copy, track=track)
        return md['msg'], jpg_buffer


class SerializingContext(zmq.Context):
    _socket_class = SerializingSocket
