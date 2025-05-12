import numpy as np

# Constantes principales: (à changer)

L1 = 10 # en cm
L2 = 10
TETA_MAX = 90
TETA_MIN = -90
PHI_MIN = -90
PHI_MAX = 90
SENSIBILITY = 0.1

# Valeurs du programme
teta = 45
phi = 45            # Ne pas oublier de convertir les angles en INT au moment de la transmission
Px = 0
Py = 0
coude : bool = 0    # Si 0 on a coude haut // 1 pour un coude bas

# Code principal :
def set_init_pos():     # Au moment de démarrer le robot
    teta = 45           # Positions connues stables
    phi = 45
    Px = L1 * np.cos(teta * np.pi / 180 ) + L2 * np.cos(teta * np.pi / 180  - phi * np.pi / 180 )
    Py = L1 * np.sin(teta * np.pi / 180 ) + L2 * np.sin(teta * np.pi / 180  - phi* np.pi / 180 )
    
    

def inverse_kinematics(new_Px, new_Py):
    # Distance au point cible
    dist = np.hypot(new_Px, new_Py)

    # Vérifier si le point est atteignable
    if dist > (L1 + L2) or dist < abs(L1 - L2):
        return 1                                       # Erreur détectée

    # Calcul de D
    D = (new_Px**2 + new_Py**2 - L1**2 - L2**2) / (2 * L1 * L2)
    D = np.clip(D, -1.0, 1.0)       # Sécurité numérique

    if coude :
        new_phi = np.arccos(D)      # Solution coude bas
    else :                      
        new_phi = -np.arccos(D)     # Solution coude haut

    new_teta = np.arctan2(new_Py, new_Px) - np.arctan2(L2 * np.sin(new_phi), L1 + L2 * np.cos(new_phi))

    # Vérifications d'angles
    if (new_teta < TETA_MIN or new_teta > TETA_MAX or new_phi < PHI_MIN or new_phi > PHI_MAX):
        return 1                                        # Erreur détectée
    
    # Ecriture des nouvelles valeurs de position + conversion en degrés
    Px = new_Px
    Py = new_Py
    teta = new_teta * 180 / np.pi
    phi = new_phi * 180 / np.pi
    
    return 0                                              # Pas d'erreur détectée


def arm_modification(x_joystick, y_joystick):
    new_Px = Px + SENSIBILITY * x_joystick
    new_Py = Py + SENSIBILITY * y_joystick
    
    if inverse_kinematics(new_Px, new_Py):
        print("Erreur détectée sur le calcul")
    
    
    
    
    
    