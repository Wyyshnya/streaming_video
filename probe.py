import cv2
from imutils.video import WebcamVideoStream

video_stream = WebcamVideoStream(src=0)
# video_stream.stream.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
# video_stream.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
# video_stream.stream.set(cv2.CAP_PROP_FPS, 24)
video_stream.start()

while(True):
    frame = video_stream.read()
    if frame.shape == (480, 640, 3):
        frame = frame[60:-60, :]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.imshow('frame', gray)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()