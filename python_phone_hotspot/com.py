import socket
import struct
import time
import cv2
import serial
from picamera2 import Picamera2

ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=0.05)

LAPTOP_IP = "10.113.193.45"  # Replace with your laptop's IP
VIDEO_PORT = 5000
CTRL_PORT = 5001

# Set up UDP socket for sending video (replaces TCP)
video_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Set up UDP socket to port 5001 for control
ctrl_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ctrl_sock.bind(("", CTRL_PORT))
ctrl_sock.settimeout(0.01)

# Set up Picamera2
picam2 = Picamera2()
config = picam2.create_preview_configuration(
    main={"size": (640, 480), "format": "RGB888"}
)
picam2.configure(config)
picam2.start()
time.sleep(0.5)

msg_length = 13
curr_data = [0 for i in range(msg_length)]

try:
    while True:
        try:
            new_data, addr = ctrl_sock.recvfrom(1024)
            print("Received data length:", len(new_data))
            if len(new_data) != msg_length:
                print(f"⚠️ Unexpected control packet size {len(new_data)}")
                continue

            ctrl_values = list(new_data)
            if curr_data != ctrl_values:
                curr_data = ctrl_values
                print(ctrl_values)
                ser.write(bytes(ctrl_values))
            
        except socket.timeout:
            pass
        
        frame = picam2.capture_array("main")
        frame = cv2.resize(frame, (320, 240))  # Resize more to reduce UDP packet size

        success, encoded = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
        if not success:
            continue

        image_bytes = encoded.tobytes()

        if len(image_bytes) > 65507:
            print("⚠️ Frame too large for UDP")
            continue

        # Header = float + int + JPEG length
        header = struct.pack("<fI", 3.14, 42)
        length = struct.pack("<I", len(image_bytes))

        packet = header + length + image_bytes

        video_sock.sendto(packet, (LAPTOP_IP, VIDEO_PORT))
        print("->")

        time.sleep(0.1)  # ~10 FPS

except (KeyboardInterrupt, Exception):
    print("\n ! Stopped by user")
    ser.write(bytes([0]*13))
finally:
    picam2.close()
    video_sock.close()
    ctrl_sock.close()
