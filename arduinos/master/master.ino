#include "Wire.h"
#include "Adafruit_PWMServoDriver.h"
#include "Servo.h"

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


const int SERVO_PIN_FR = 11;
const int SERVO_PIN_BR = 10;
const int SERVO_PIN_FL = 6;
const int SERVO_PIN_BL = 5;

byte  data_slave1[l_data_slv1];
byte  data_slave2[l_data_slv2];
uint8_t   data_Servos[l_data_Serv] = {0};
bool  transmission_allowed = 0;

bool servo_change = false;

///
void  sendArmServosData();
int   angleToPulse(int ang);
void  read_data();
void  sendToNano(byte address, byte data[], int length);
void  sendArmServosData();
int   angleToPulse(int ang);

Servo serv_FR;
Servo serv_BR;
Servo serv_FL;
Servo serv_BL;

///

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
}

void loop()
{
  transmission_allowed = 0;
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

    if (new_val != data_Servos[i]) {
      data_Servos[i] = new_val;
      servo_change = true;
    }
  }

  Serial.write(data_slave1, l_data_slv1);
  Serial.write(data_slave2, l_data_slv2);
  Serial.write(data_Servos, l_data_Serv);

  data_Servos[l_data_Serv - 1] = int(data_Servos[l_data_Serv - 1] * 3.937);      // Conversion pour le gripper du bras
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
