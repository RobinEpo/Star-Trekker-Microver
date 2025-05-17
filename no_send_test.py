import pygame
from pygame.locals import *
import serial
import direction as dir
import struct
import time


pygame.init()
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
deadzone = 0.1
 
speed_r = 0
speed_l = 0
angle = 90

data_slave1 = [0, 0, 0]     # signed 8-bit
data_slave2 = [0, 0, 0]     # signed 8-bit
data_servos = [90, 90, 90, 90]
curr_data = [data_slave1, data_slave2, data_servos]

while True:
    for event in pygame.event.get() :
        if event.type == JOYAXISMOTION :
            if event.axis == 0 : #joystick = event 0
                if abs(event.value) > deadzone:
                    angle = (int(90*(1+event.value)))
                else:
                    angle = 90
            if event.axis == 2 : #left trigger = event 4
                speed_r = (int(-255*(event.value+1)/2))
            if event.axis == 5 : #right trigger = event 5
                speed_l = (int(255*(event.value+1)/2))

    speed = int((speed_r + speed_l)/2)  
    data_slave1 = [speed, speed, speed]
    data_slave2 = [speed, speed, speed]
    data_servos = [angle, angle, angle, angle]
    new_data = [data_slave1, data_slave2, data_servos]

    #Debug note: Already verified that only one bit is sent each time
    if (new_data != curr_data):
        curr_data = new_data
        for spd in data_slave1:
            a = 1
        for spd in data_slave2:
            a = 1
        for angle in data_servos:
            a = 1

        time.sleep(0.001)
        print(f"Sent : Speed = {speed}, angle = {angle}")
        for i in range(12):
            a = 1

def transmit_direction():
    data_dir = [dir.MotorFR, dir.MotorMR, dir.MotorBR, dir.MotorFL, dir.MotorML, 
                dir.MotorBL, dir.ServoFR, dir.ServoBR, dir.ServoFL, dir.ServoBL]   
    ser.write(bytes(data_dir))

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