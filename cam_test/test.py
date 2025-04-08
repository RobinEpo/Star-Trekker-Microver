import socket
import cv2

server_ip = "127.0.0.1"
server_port = 4242

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()

    if not ret:
        print("Error: failed to capture image")
        break

    frame = cv2.resize(frame, (400, 300))
    frame = cv2.flip(frame, 1)

    cv2.putText(
        frame,
        f"OpenCV version: {cv2.__version__}",
        (5, 15),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (255, 255, 255),
        1,
    )
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    canny = cv2.Canny(blur, 20, 50)
    canny = cv2.cvtColor(canny, cv2.COLOR_GRAY2BGR)

    row1 = cv2.hconcat([frame, gray])
    row2 = cv2.hconcat([blur, canny])
    image = cv2.vconcat([row1, row2])

    image = cv2.resize(image, (400, 300))

    _, encoded_frame = cv2.imencode(".jpg", image)

    if len(encoded_frame) <= 65507:
        client_socket.sendto(encoded_frame, (server_ip, server_port))
    else:
        print("Frame too large, skipping")

    cv2.imshow("frame", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cv2.destroyAllWindows()

cap.release()