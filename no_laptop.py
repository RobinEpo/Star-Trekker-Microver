import pygame
from pygame.locals import *
import serial
import direction as dir
import struct
import time

ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=0.05)

pygame.init()

pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
deadzone = 0.1
 
speed_r = 0
speed_l = 0
angle = 90

data_slave1 = [0, 0, 0]     # signed 8-bit
data_slave2 = [0, 0, 0]     # signed 8-bit
data_servos = [angle, angle, angle, angle]
all_data = [data_slave1, data_slave2, data_servos]


def transmit_direction():
    data_dir = [dir.MotorFR, dir.MotorMR, dir.MotorBR, dir.MotorFL, dir.MotorML, 
                dir.MotorBL, dir.ServoFR, dir.ServoBR, dir.ServoFL, dir.ServoBL]   
    ser.write(bytes(data_dir))

while True:
    for event in pygame.event.get() :
        if event.type == JOYAXISMOTION :
            if event.axis == 0 : #joystick
                if abs(event.value) > deadzone:
                    angle = (int(90*(1+event.value)))
                else:
                    angle = 90
            if event.axis == 4 : #left trigger
                speed_r = (int(-(event.value+1)*255/2))
            if event.axis == 5 : #right trigger
                speed_l = (int(255*(event.value+1)/2))

    speed = int((speed_r + speed_l)/2) + 128 # 4 
    data_slave1 = [speed, speed, speed]     # signed 8-bit
    data_slave2 = [speed, speed, speed]     # signed 8-bit
    data_servos = [angle, angle, angle, angle]
    new_data = [data_slave1, data_slave2, data_servos]

    if (new_data != all_data):
        all_data = new_data
        for pack in all_data:
            for item in pack:
                ser.write(bytes([item]))
                print((bytes([item])), end=" ")
        time.sleep(0.001)
        print(f"Sent : Speed = {speed}, angle = {angle}")

    # dir.Input_speed = speed
    # dir.x_joystick = angle
    # dir.calculate_transmission()
    # transmit_direction()



    # if event.type == JOYBUTTONDOWN :
    #     if event.button == 4 : #left_bumper down
    #         print("left_bumper_down")
    #     if event.button == 5 : #right bumper down
    #         print("right_bumper_down")
    # if event.type == JOYBUTTONUP :
    #     if event.button == 4 : #left_bumper up
    #         print("left_bumper_up")
    #     if event.button == 5 : #right_bumper up
    #         print("right_bumper_up")