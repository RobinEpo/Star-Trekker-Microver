import pygame
from pygame.locals import *
import serial
import direction as dir
import arm
import struct
import time

ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=0.05)     # '/dev/ttyUSB0' sur linux ; 'COM3' sur WINDOWS

# Constantes des boutons manette : 
Bouton_A : int = 0
Bouton_B : int = 1
Bouton_X : int = 2
Bouton_Y : int = 3
Bouton_Joystick_Left : int = 9          # 10 si manette PS4 / 9 si Xbox
Bouton_Joystick_Right : int = 10        # 11 si manette PS4 / 10 si Xbox

# Constantes des axes manette : 
X_Left_Joystick : int = 0               
Gachette_Gauche : int = 2               # 3 si PS4 / 2 si Xbox
Gachette_Droite : int = 5               # 4 si PS4 / 5 si Xbox

pygame.init()
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
deadzone = 0.1

speed_r = 0
speed_l = 0
speed_gripper = 0
speed_gripper_r = 0
speed_gripper_l = 0
x_joystick = 0
y_joystick = 0
angle = 90
mode : bool = 0         # 0 pour course / 1 pour bras
B_Pressed : bool = 0    # Pour le boost
mode_coude : bool = 0

data_slave1 = [0, 0, 0]     # signed 8-bit
data_slave2 = [0, 0, 0]     # signed 8-bit
data_servos = [90, 90, 90, 90]
curr_data = [data_slave1, data_slave2, data_servos]

arm.set_init_pos()

while True:
    for event in pygame.event.get() :
        if event.type == JOYAXISMOTION :
            if event.axis == 0 :                # x axis
                if abs(event.value) > deadzone:
                    #  angle = (int(90*(1+event.value)))
                    x_joystick = event.value
                else:
                    x_joystick = 0
            if event.axis == 1 :                # y axis 
                if abs(event.value) > deadzone:
                    y_joystick = -event.value           # - car le signal est inversé (1 en bas et -1 en haut)
                else:
                    y_joystick = 0
            if event.axis == 5 and mode == 0:           #left trigger = event 4
                speed_r = (int(255*(event.value+1)/2))
            if event.axis == 2 and mode == 0:           #right trigger = event 5
                speed_l = (int(-255*(event.value+1)/2))
            if event.axis == 5 and mode == 1:           #left trigger = event 4
                speed_gripper_r = (event.value + 1)/2
                if speed_gripper_r < 0:
                    speed_gripper_r = 0
            if event.axis == 2 and mode == 1:           #right trigger = event 5
                speed_gripper_l = -(event.value + 1)/2
                if speed_gripper_l < 0:
                    speed_gripper_l = 0
            
        if event.type == JOYBUTTONDOWN: 
            if event.button == Bouton_Y:       # Bouton Y
                mode = not mode         # Switch entre mode déplacement / bras 
                print("Bouton Y pressé")
            if event.button == Bouton_B:       # Bouton B
                B_Pressed = 1           # Activation boost (race mode)
                print("Bouton B pressé")
            if event.button == Bouton_A:       
                arm.coude = not arm.coude
                print("Bouton A pressé")
                
        if event.type == JOYBUTTONUP:
            if event.button == 1:       # Bouton B
                B_Pressed = 0           # Stop boost (precision mode)
                print("Bouton B relâché")
            
    if B_Pressed:                          # Boost si on est en mode racing
        speed = int((speed_r + speed_l)/2)
    else : 
        speed = int((speed_r + speed_l)/4)
    speed_gripper = int((speed_gripper_l + speed_gripper_r) * 127)
    
    print("mode = ", mode)
    if mode == 0:
        speed_gripper = 0                   # Empêcher la modification de la pince quand on roule
        dir.x_joystick = x_joystick
        dir.Input_speed = speed
        dir.mode = B_Pressed
        dir.calculate_transmission()
     
    # data_slave1 = [speed, speed, speed]
    # data_slave2 = [speed, speed, speed]
    # data_servos = [angle, angle, angle, angle]
    # new_data = [data_slave1, data_slave2, data_servos]
    
    else :
        arm.arm_modification(x_joystick, y_joystick)
    
    data_slaves = [dir.MotorFR, dir.MotorMR, dir.MotorBR, dir.MotorFL, dir.MotorML, 
                    dir.MotorBL]
    data_servos = [dir.ServoFR, dir.ServoBR, dir.ServoFL, dir.ServoBL]
    data_arm = [arm.teta + 90, arm.phi + 90]                            # shift nécessaire car calculs de -90° à 90° sur arm.py
    new_data = [data_slaves, data_servos, data_arm]
    
    #Debug note: Already verified that only one bit is sent each time
    
    if (new_data != curr_data):
        curr_data = new_data
        for spd in data_slaves:
            ser.write(int(spd).to_bytes(1, byteorder='big', signed=True))
        for angle in data_servos:
            ser.write(int(angle).to_bytes(1, byteorder='big', signed=False))
        for angle in data_arm:
            ser.write(int(angle).to_bytes(1, byteorder='big', signed=False))
        ser.write(int(speed_gripper).to_bytes(1, byteorder='big', signed=True))

        time.sleep(0.1)
        print(f"Sent : Speed = {speed}, angle = {angle}")
        for i in range(13):
            print(ser.read().hex(), end=" ") 
    

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
