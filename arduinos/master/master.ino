#include "Wire.h"
#include <Adafruit_PWMServoDriver.h>

// NOTE : Consider adding sleep mode when servo_change is false

#define SERVOMIN  125 // this is the 'minimum' pulse length count (out of 4096)
#define SERVOMAX  625 // this is the 'maximum' pulse length count (out of 4096) 

const int l_data_slv1 = 3;
const int l_data_slv2 = 3;
const int l_data_Serv = 4;
const int tot_data_length = l_data_Serv + l_data_slv1 + l_data_slv2;

const byte adress_slave1 = 0x01;
const byte adress_slave2 = 0x02;
Adafruit_PWMServoDriver splitter = Adafruit_PWMServoDriver(0x40);


byte  data_slave1[l_data_slv1];
byte  data_slave2[l_data_slv2];
uint8_t   data_Servos[l_data_Serv] = {0};
bool  transmission_allowed = 0;

bool servo_change = false;

///
void  sendServosData();
int   angleToPulse(int ang);
void  read_data();
void  sendToNano(byte address, byte data[], int length);
void  sendServosData();
int   angleToPulse(int ang);
///

void setup() 
{
  Serial.begin(9600);                                                                                                                                                                                                                                                         
  Wire.begin();
  splitter.begin();
  splitter.setPWMFreq(60);
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
      sendServosData();
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
}

void sendToNano(byte address, byte data[], int length) {
  Wire.beginTransmission(address);
  Wire.write(data, length);
  Wire.endTransmission();
}

void sendServosData()
{
  for (unsigned i = 0; i < l_data_Serv; i++) {
    splitter.setPWM(i, 0, angleToPulse(data_Servos[i]));
  }
}

int angleToPulse(int ang) {                            //gets the angle in degree and returns the pulse width  
  int pulse = map(ang,0, 180, SERVOMIN,SERVOMAX);  // map angle of 0 to 180 to Servo min and Servo max 
  return pulse;
}