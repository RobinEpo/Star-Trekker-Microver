# tcp_receiver_and_udp_forwarder.py
import socket
import struct
import cv2
import numpy as np

# TCP server settings
HOST = "0.0.0.0"
TCP_PORT = 5000

# UDP settings for Godot
GODOT_IP = "127.0.0.1"
GODOT_PORT = 4242

# Start TCP server (receives frames from Raspberry Pi)
tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_sock.bind((HOST, TCP_PORT))
tcp_sock.listen(1)

print("📡 Waiting for Raspberry Pi to connect...")
conn, addr = tcp_sock.accept()
print("✅ TCP connected from", addr)

# Start UDP socket (to forward frames to Godot)
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Helper: receive exactly n bytes
def recv_exact(sock, num_bytes):
    data = b""
    while len(data) < num_bytes:
        chunk = sock.recv(num_bytes - len(data))
        if not chunk:
            return None
        data += chunk
    return data

while True:
    # Step 1: header = float (4 bytes) + int (4 bytes)
    header = recv_exact(conn, 8)
    if not header:
        break
    float_val, int_val = struct.unpack("<fI", header)

    # Step 2: JPEG size (4 bytes)
    length_bytes = recv_exact(conn, 4)
    if not length_bytes:
        break
    image_size = struct.unpack("<I", length_bytes)[0]

    # Step 3: JPEG data
    image_data = recv_exact(conn, image_size)
    if not image_data:
        break

    # Optional: Show the image in OpenCV (debug)
    np_data = np.frombuffer(image_data, dtype=np.uint8)
    frame = cv2.imdecode(np_data, cv2.IMREAD_COLOR)
   # if frame is not None:
    #    cv2.imshow("TCP Received", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # Step 4: Forward the header + image to Godot via UDP
    udp_packet = header + image_data
    if len(udp_packet) <= 65507:
        udp_sock.sendto(udp_packet, (GODOT_IP, GODOT_PORT))
        print("📤 Forwarded frame to Godot")
    else:
        print("⚠️ Packet too large for UDP")

conn.close()
tcp_sock.close()
udp_sock.close()
cv2.destroyAllWindows()
