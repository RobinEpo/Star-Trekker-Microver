#include "Wire.h"
#include "Adafruit_PWMServoDriver.h"
#include "Servo.h"
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <EEPROM.h>

Adafruit_BNO055 bno = Adafruit_BNO055(55);
const int EEPROM_ADDR = 0;
bool offsetsRestored = false;

volatile unsigned long startTime = 0;
volatile unsigned long endTime = 0;
volatile bool measurementReady = false;

const int trigPin = 3;
const int echoPin = 2; // Doit être une pin d’interruption sur le Nano (D2 = INT0)

// NOTE : Consider adding sleep mode when servo_change is false

#define SERVOMIN  125 // this is the 'minimum' pulse length count (out of 4096)
#define SERVOMAX  625 // this is the 'maximum' pulse length count (out of 4096) 

const int l_data_slv1 = 3;
const int l_data_slv2 = 3;
const int l_data_Serv = 7;
const int tot_data_length = l_data_Serv + l_data_slv1 + l_data_slv2;

const byte adress_slave1 = 0x01;
const byte adress_slave2 = 0x02;
Adafruit_PWMServoDriver splitter = Adafruit_PWMServoDriver(0x40);


const int SERVO_PIN_FR = 10;            // 11
const int SERVO_PIN_BR = 11;            // 10
const int SERVO_PIN_FL = 6;             // 6
const int SERVO_PIN_BL = 5;             // 5

byte  data_slave1[l_data_slv1];
byte  data_slave2[l_data_slv2];
uint8_t   data_Servos[l_data_Serv] = {0};
bool  transmission_allowed = 0;

bool servo_change = false;

///
void  sendWheelServosData();
int   angleToPulse(int ang);
void  read_data();
void  sendToNano(byte address, byte data[], int length);
void  sendArmServosData();
int   angleToPulse(int ang);

Servo serv_FR;
Servo serv_BR;
Servo serv_FL;
Servo serv_BL;

float lastDistance(0);

///
void triggerUltrasound() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
}



void setup() 
{
  Serial.begin(9600);                                                                                                                                                                                                                                                         
  Wire.begin();
  splitter.begin();
  splitter.setPWMFreq(60);

  serv_FR.attach(SERVO_PIN_FR);
  serv_BR.attach(SERVO_PIN_BR);
  serv_FL.attach(SERVO_PIN_FL);
  serv_BL.attach(SERVO_PIN_BL);

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  attachInterrupt(digitalPinToInterrupt(echoPin), echoISR, CHANGE);

  if (!bno.begin()) {
    Serial.println("Erreur : BNO055 non détecté !");
    while (1);
  }

  bno.setExtCrystalUse(true);
  delay(1000);

  // Charger les offsets depuis EEPROM
  adafruit_bno055_offsets_t storedOffsets;
  EEPROM.get(EEPROM_ADDR, storedOffsets);

  if (isValidOffsets(storedOffsets)) {
    bno.setSensorOffsets(storedOffsets);
    offsetsRestored = true;
    Serial.println("Offsets restaurés depuis EEPROM.");
  } else {
    Serial.println("Offsets non valides. Calibration requise...");
  }
}

void loop()
{
  // Serial.println(Serial.available());
  if (Serial.available() >= tot_data_length)
  {
    read_data();

    sendToNano(adress_slave1, data_slave1, l_data_slv1);
    sendToNano(adress_slave2, data_slave2, l_data_slv2);
    if (servo_change)
    {
      sendWheelServosData();
      sendArmServosData();    
      servo_change = false;
    }
  }
  
  // Capteur Ultrasons :

  if (!measurementReady){
    triggerUltrasound();
  }

  if (measurementReady) {
    measurementReady = false;
    Serial.println(lastDistance);
  }

  // IMU :

  if (!offsetsRestored) {
    uint8_t sys, gyro, accel, mag;
    bno.getCalibration(&sys, &gyro, &accel, &mag);

    Serial.print("Calib (SYS,G,A,M): ");
    Serial.print(sys); Serial.print(" ");
    Serial.print(gyro); Serial.print(" ");
    Serial.print(accel); Serial.print(" ");
    Serial.println(mag);

    if (sys == 3 && gyro == 3 && accel == 3 && mag == 3) {
      adafruit_bno055_offsets_t calib;
      bno.getSensorOffsets(calib);
      EEPROM.put(EEPROM_ADDR, calib);
      Serial.println("✅ Calibration terminée. Offsets sauvegardés !");
      offsetsRestored = true;
      delay(1000);
    }
  } else {
    // Utilisation normale : par exemple lire les quaternions
    imu::Quaternion quat = bno.getQuat();
    Serial.print("QUAT:");
    Serial.print(quat.w(), 4); Serial.print(",");
    Serial.print(quat.x(), 4); Serial.print(",");
    Serial.print(quat.y(), 4); Serial.print(",");
    Serial.println(quat.z(), 4);
  }


  delay(10);
}

// Création des fonctions de transmission de données : 


void read_data() //Confirmed works as intended
{
  for (int i(0); i < l_data_slv1; i++) {
    data_slave1[i] = Serial.read();
  }
  for (int i(0); i < l_data_slv2; i++) {
    data_slave2[i] = Serial.read();
  }
  for (int i(0); i < l_data_Serv; i++) {
    uint8_t new_val(Serial.read());

    if (new_val != data_Servos[i] and new_val != 200) {
      data_Servos[i] = new_val;
      servo_change = true;
    }
    else if (new_val == 200){
      resetCalibration();
    }
  }


  // data_Servos[l_data_Serv - 1] = (int)(data_Servos[l_data_Serv - 1] * 3.937);   DEBUG   // Conversion pour le gripper du bras
}

void sendToNano(byte address, byte data[], int length) {
  Wire.beginTransmission(address);
  Wire.write(data, length);
  Wire.endTransmission();
}

void sendWheelServosData()
{
  serv_FR.write(data_Servos[0]);
  serv_BR.write(data_Servos[1]);
  serv_FL.write(data_Servos[2]);
  serv_BL.write(data_Servos[3]);
}

void sendArmServosData()
{
  for (unsigned i = 4; i < l_data_Serv; i++) {          // Attention à changer pour le gripper (servira pour les connexions du bras)
    splitter.setPWM(i, 0, angleToPulse(data_Servos[i]));
  }
}

int angleToPulse(int ang) {                            //gets the angle in degree and returns the pulse width  
  int pulse = map(ang,0, 180, SERVOMIN,SERVOMAX);  // map angle of 0 to 180 to Servo min and Servo max 
  return pulse;
}


// Ultrasons :
// Cette fonction est appelée à chaque changement d’état sur Echo (front montant et descendant)
void echoISR() {
  if (digitalRead(echoPin) == HIGH) {
    startTime = micros();
  } else {
    endTime = micros();
    unsigned long duration = endTime - startTime;

    if (duration > 100) {
      lastDistance = duration / 58.0;
      measurementReady = true;
    }
  }
}


// IMU : 

// Vérifie si les offsets sont plausibles (simple heuristique)
bool isValidOffsets(const adafruit_bno055_offsets_t& data) {
  // Un offset vierge a souvent tous les champs à 0 ou 0xFFFF
  return !(data.accel_offset_x == 0 && data.gyro_offset_x == 0);
}

void resetCalibration() {
  adafruit_bno055_offsets_t emptyOffsets;
  EEPROM.put(EEPROM_ADDR, emptyOffsets);

  offsetsRestored = false; // Forcer recalibration
}
