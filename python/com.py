import socket
import struct
import time
import cv2
import serial
from picamera2 import Picamera2

ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=0.05)

LAPTOP_IP = "10.113.193.45"  # Replace with your laptop's IP
PORT = 5000

# Set up TCP socket and connect to laptop
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((LAPTOP_IP, PORT))
print("o Connected to laptop")

# Set up UDP socket to port 5001
ctrl_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ctrl_sock.bind(("", 5001))
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
            # data is a bytes object; expect len(data) == 13
            print("Received data length:", len(new_data))
            if len(new_data) != msg_length:
                print(f"⚠️ Unexpected control packet size {len(new_data)}")
                continue

            # 3) Parse the 13 bytes into ints 0–255
            ctrl_values = list(new_data)
            if curr_data != ctrl_values:
                curr_data = ctrl_values
                print(ctrl_values)
                ser.write(bytes(ctrl_values))
            
        except socket.timeout:
            pass
        
        frame = picam2.capture_array("main")
        frame = cv2.resize(frame, (400, 300))

        success, encoded = cv2.imencode(".jpg", frame)
        if not success:
            continue

        image_bytes = encoded.tobytes()

        # Header = float + int + JPEG length
        header = struct.pack("<fI", 3.14, 42) #< means little endian, f means float, I means Int
        length = struct.pack("<I", len(image_bytes))

        # Send complete packet
        sock.sendall(header + length + image_bytes)
        print("->")

        time.sleep(0.02)  # ~50 FPS

except (KeyboardInterrupt, Exception):
    print("\n ! Stopped by user")
    ser.write(bytes([0]*13))   # all zeros
finally:
    picam2.close()
    sock.close()
    picam2.close()