import socket
import struct
import time
import threading
import cv2
import serial
from picamera2 import Picamera2

# ── Configuration ─────────────────────────────────────────────────────────────
LAPTOP_IP = "10.113.193.45"   # Laptop's IP address
TCP_PORT   = 5000              # Port for video stream
CONTROL_PORT = 5001            # Port for control commands
MSG_LENGTH = 13                # Expected length of each control packet

# Serial port to microcontroller
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=0.05)

# TCP socket for video
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((LAPTOP_IP, TCP_PORT))
print("● Connected to laptop for video stream")

# UDP socket for control
ctrl_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ctrl_sock.bind(("", CONTROL_PORT))
ctrl_sock.settimeout(0.01)
print(f"● Listening for control on UDP port {CONTROL_PORT}")

# Picamera2 setup
picam2 = Picamera2()
config = picam2.create_preview_configuration(
    main={"size": (640, 480), "format": "RGB888"}
)
picam2.configure(config)
picam2.start()
time.sleep(0.5)

# Shared state
last_ctrl_time = time.time()
curr_data = [0] * MSG_LENGTH
ctrl_lock = threading.Lock()


def control_listener():
    global last_ctrl_time, curr_data
    while True:
        try:
            pkt, _ = ctrl_sock.recvfrom(1024)
            if len(pkt) == MSG_LENGTH:
                vals = list(pkt)
                with ctrl_lock:
                    curr_data = vals
                    ser.write(bytes(curr_data))
                    last_ctrl_time = time.time()
        except socket.timeout:
            pass

        # Watchdog: if no update in 200 ms, stop motors
        if time.time() - last_ctrl_time > 0.2:
            with ctrl_lock:
                if any(curr_data):
                    curr_data = [0] * MSG_LENGTH
                    ser.write(bytes(curr_data))
        time.sleep(0.01)


def video_streamer():
    while True:
        try:
            print("📡 Connecting to laptop for video stream...")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((LAPTOP_IP, PORT))
            print("✅ Connected to laptop")

            while True:
                try:
                    frame = picam2.capture_array("main")
                    frame = cv2.resize(frame, (400, 300))

                    success, encoded = cv2.imencode(".jpg", frame)
                    if not success:
                        continue

                    image_bytes = encoded.tobytes()
                    header = struct.pack("<fI", 3.14, 42)
                    length = struct.pack("<I", len(image_bytes))
                    sock.sendall(header + length + image_bytes)
                    time.sleep(0.02)  # ~50 FPS
                except Exception as e:
                    print(f"⚠️ Streaming error: {e}")
                    break  # Exit inner loop, reconnect
        except Exception as e:
            print(f"❌ TCP connection failed: {e}")
        time.sleep(2)  # Wait before retrying


if __name__ == '__main__':
    # Start threads
    t_ctrl  = threading.Thread(target=control_listener, daemon=True)
    t_video = threading.Thread(target=video_streamer, daemon=True)
    t_ctrl.start()
    t_video.start()

    # Keep main alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n■ Interrupted by user — stopping motors")
        ser.write(bytes([0] * MSG_LENGTH))
    finally:
        picam2.close()
        sock.close()
        ser.close()
