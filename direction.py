import math as m

# Geometrical considerations :
LENGTH_1 = 15          # Valeur de test à changer (en cm)
LENGTH_2 = LENGTH_1
WIDTH = 20             # Valeur de test à changer (en cm)
DELTA_WIDTH = 0.2
MAX_ANGLE_RACING = 20 * m.pi / 180 # En radians direct (plus utile pour les calculs)
MAX_ANGLE_PRECISION = m.pi / 2
ANGLE_FRONT = 90        # A vérif (degrés)

# Input states :
rotation : bool = 0    # 1 si on tourne
direction : bool = 0   # 0 = gauche / 1 = droite
mode : bool = 0        # 0 = Precision / 1 = Race
x_joystick = 0         # On suppose de -1 à 1 --> Réajuster sinon
Input_speed = 0


# Output states : 
MotorFR : int = 0   # Front Right
MotorMR : int = 0   # Middle Right
MotorBR : int = 0   # Back Right
MotorFL : int = 0
MotorML : int = 0
MotorBL : int = 0

ServoFR : int = 0
ServoBR : int = 0
ServoFL : int = 0
ServoBL : int = 0


def Calculate_Radius(): # Rayon intérieur de courbure
    angle = 0
    
    # On cherche à avoir le rayon avec un angle qui varie linéairement :
    if mode == 0 :      # Precision
        angle = abs(x_joystick) * MAX_ANGLE_PRECISION
    else :              # Racing
        angle = abs(x_joystick) * MAX_ANGLE_RACING
    
    Radius = (LENGTH_1 + LENGTH_2) / (2 * m.sin(angle))
    
    return Radius




# Début code principal : 
def calculate_transmission() :
    global MotorFR, MotorMR, MotorBR, MotorFL, MotorML, MotorBL
    global ServoFR, ServoBR, ServoFL, ServoBL
    global rotation, direction
    
    if x_joystick == 0 :
        rotation = 0
        
        MotorFR = Input_speed 
        MotorMR = Input_speed   
        MotorBR = Input_speed    
        MotorFL = Input_speed 
        MotorML = Input_speed 
        MotorBL = Input_speed 
        
        ServoFR = ANGLE_FRONT
        ServoBR = ANGLE_FRONT
        ServoFL = ANGLE_FRONT
        ServoBL = ANGLE_FRONT
        

    elif x_joystick > 0 : # Tourne à droite
        rotation = 1 
        direction = 1
        
        radius = Calculate_Radius()   # Rayon roues avant et arrière droite
        in_angle = m.asin((LENGTH_1 + LENGTH_2) / (2 * radius))
        ext_radius = radius + WIDTH * m.cos(in_angle)  # Rayon roues avant et arrière gauche
        ext_angle = m.asin((LENGTH_1 + LENGTH_2) / (2 * ext_radius))
        
        
        # Moteurs :
        MotorFL = Input_speed
        MotorBL = Input_speed
        
        MotorFR = Input_speed * radius / ext_radius
        MotorBR = Input_speed * radius / ext_radius

        MotorMR = Input_speed * (m.sqrt(1 - ((LENGTH_1 + LENGTH_2) / (2 * radius)) ** 2 ) - DELTA_WIDTH / radius)
        MotorML = Input_speed * (m.sqrt(1 - ((LENGTH_1 + LENGTH_2) / (2 * ext_radius)) ** 2 ) + DELTA_WIDTH / ext_radius)
        
        # Servos : 
        ServoFR = ANGLE_FRONT + in_angle * 180 / m.pi
        ServoBR = ANGLE_FRONT + in_angle * 180 / m.pi
        ServoFL = ANGLE_FRONT + ext_angle * 180 / m.pi
        ServoBL = ANGLE_FRONT + ext_angle * 180 / m.pi
        
        
        
        
    else :                 # Tourne à gauche
        rotation = 1 
        direction = 0
        
        radius = Calculate_Radius()                                 # Rayon roue avant et arrière gauche
        in_angle = m.asin((LENGTH_1 + LENGTH_2) / (2 * radius))
        ext_radius = radius + WIDTH * m.cos(in_angle)               # Rayon roues avant et arrière droite
        ext_angle = m.asin((LENGTH_1 + LENGTH_2) / (2 * ext_radius))
        
        # Moteurs :
        MotorFR = Input_speed
        MotorBR = Input_speed
        
        MotorFL = Input_speed * radius / ext_radius
        MotorBL = Input_speed * radius / ext_radius
        
        MotorMR = Input_speed * (m.sqrt(1 - ((LENGTH_1 + LENGTH_2) / (2 * ext_radius)) ** 2 ) + DELTA_WIDTH / ext_radius)
        MotorML = Input_speed * (m.sqrt(1 - ((LENGTH_1 + LENGTH_2) / (2 * radius)) ** 2 ) - DELTA_WIDTH / radius)
        
        # Servos :                          # Adapter les angles selon l'orientation du servo
        ServoFR = ANGLE_FRONT - ext_angle * 180 / m.pi
        ServoBR = ANGLE_FRONT - ext_angle * 180 / m.pi
        ServoFL = ANGLE_FRONT - in_angle * 180 / m.pi
        ServoBL = ANGLE_FRONT - in_angle * 180 / m.pi
    
     # print(MotorFR, MotorMR, MotorBR, MotorFL, MotorML, MotorBL, ServoFR, ServoBR, ServoFL, ServoBL)
        
def invert_mode():
    global mode
    mode = not mode

   
# Il manque simplement la réception des données depuis la manette et son traitement. A voir si on utilise un
# nouveau GitHub pour la réception. 
