import socket
import pygame
from pygame.locals import *
import direction as dir
import arm
import time
from constants import *

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

#Create a UDP socket
CONTROL_IP = "10.113.193.143"   # RPi’s IP
CONTROL_PORT = 5001
udp_ctrl_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

pygame.init()
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
deadzone = 0.1

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
    
    else :
        arm.arm_modification(x_joystick, y_joystick)
    
    data_slaves = [dir.MotorFR, dir.MotorMR, dir.MotorBR, dir.MotorFL, dir.MotorML, 
                    dir.MotorBL]
    data_slaves_b = [int(elem).to_bytes(1, byteorder='big', signed=True) for elem in data_slaves]
    data_servos = [dir.ServoFR, dir.ServoBR, dir.ServoFL, dir.ServoBL]
    data_servos_b = [int(elem).to_bytes(1, byteorder='big', signed=False) for elem in data_servos]
    data_arm = [arm.teta + 90, arm.phi + 90]                            # shift nécessaire car calculs de -90° à 90° sur arm.py
    data_arm_b = [int(elem).to_bytes(1, byteorder='big', signed=False) for elem in data_arm]
    placeholder = [speed_gripper.to_bytes(1, byteorder='big', signed=True)]

    ctrl_bytes =  b"".join(data_slaves_b + data_servos_b + data_arm_b + placeholder)
    udp_ctrl_sock.sendto(ctrl_bytes, (CONTROL_IP, CONTROL_PORT))
    time.sleep(0.1)
