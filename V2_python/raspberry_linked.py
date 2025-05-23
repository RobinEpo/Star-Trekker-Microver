# traitement.py (exécuté en continu sur la Pi ou via crontab/systemd)
import json
import time
import struct
import serial

LENGTH_DATA = 13

ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=0.05)     # '/dev/ttyUSB0' sur linux ; 'COM3' sur WINDOWS
curr_data = [0] * LENGTH_DATA

fmt = "6b4B2Bb"  # même format que laptop.py  --> b => signé / B => non signé

while True:
    try:
        with open("/home/pi/input_data.bin", "rb") as f:
            content = f.read()

        if len(content) == LENGTH_DATA:
            data = struct.unpack(fmt, content)

            data_slaves = data[0:6]   # int8 signés
            data_servos = data[6:10]  # uint8 non signés
            data_arm = data[10:12]    # uint8 non signés
            speed_gripper = data[12]  # int8 signé

            # Envoi via série
            for spd in data_slaves:
                ser.write(spd.to_bytes(1, byteorder='big', signed=True))

            for angle in data_servos:
                ser.write(angle.to_bytes(1, byteorder='big', signed=False))

            for angle in data_arm:
                ser.write(angle.to_bytes(1, byteorder='big', signed=False))

            ser.write(speed_gripper.to_bytes(1, byteorder='big', signed=True))

        time.sleep(0.1)

    except Exception as e:
        print("Erreur :", e)
    time.sleep(0.05)
