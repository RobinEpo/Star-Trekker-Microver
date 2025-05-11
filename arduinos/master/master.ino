#include "Wire.h"
#include <Adafruit_PWMServoDriver.h>

// NOTE : Consider adding sleep mode when servo_change is false

#define SERVOMIN  125 // this is the 'minimum' pulse length count (out of 4096)
#define SERVOMAX  625 // this is the 'maximum' pulse length count (out of 4096) 

const int length_data_Servos = 4;
const int length_data_slave1 = 3;
const int length_data_slave2 = 3;
const int nbr_data_expected = length_data_Servos + length_data_slave1 + length_data_slave2;

const byte adress_slave1 = 0x01;
const byte adress_slave2 = 0x02;
Adafruit_PWMServoDriver board = Adafruit_PWMServoDriver(0x40);


int data_Servos[length_data_Servos] = {0};
byte data_slave1[length_data_slave1];
byte data_slave2[length_data_slave2];
bool transmission_allowed = 0;

// Création des fonctions de transmission de données : 

bool servo_change = false;
void sendServosData();
int angleToPulse(int ang);

void read_data()
{
  for (int i = 0; i<nbr_data_expected; ++i)
    {
      if (i < length_data_slave1)
      {
        data_slave1[i] = (int)Serial.read();
        continue;
      }

      if (i >= length_data_slave1 and (i < length_data_slave2 + length_data_slave1))
      {
        data_slave2[i-length_data_slave1] = (int)Serial.read();
        continue;
      }

      if (i >= (length_data_slave2 + length_data_slave1))
      {
        int new_val(Serial.read());
        int j(i-length_data_slave2 - length_data_slave1);

        if (new_val != data_Servos[j])
        {
          data_Servos[j] = new_val;
          servo_change = true;
        }

      }      
    }
    // for (int i(0); i < 3; i++)
    // {
    //   Serial.print(data_slave1[i]);
    //   Serial.print(data_slave2[i]);
    // }
  
  transmission_allowed = 1;

}


void sendToNano(byte address, byte data[], int length) {
  Wire.beginTransmission(address);
  Wire.write(data, length);
  // Serial.print("Sending to Nano value ");
  // for (unsigned i(0); i < 3; i++)
  // {
  //   Serial.print((int8_t)(*(data+i)));
  //   Serial.print(" ");
  // }
  // Serial.println();
  Wire.endTransmission();
}


// Fonctions principales du programme : 


void setup() 
{
  Serial.begin(9600);                                                                                                                                                                                                                                                         
  Wire.begin();
}

int j(0);
void loop()
{
  transmission_allowed = 0;

  if (Serial.available() >= nbr_data_expected)
  {
    read_data();

    if (transmission_allowed)
    {
      sendToNano(adress_slave1, data_slave1, length_data_slave1);
      sendToNano(adress_slave2, data_slave2, length_data_slave2);
      if (servo_change)
      {
        // sendServosData();
      }
      transmission_allowed = 0;
    }
  }
  delay(1);
}

// void sendServosData()
// {
//   for (unsigned i = 0; i < length_data_Servos; i++)
//   {
//     board.setPWM(i, 0, angleToPulse(data_Servos[i]));
//   }
// }

// int angleToPulse(int ang) {                            //gets the angle in degree and returns the pulse width  
//   int pulse = map(ang,0, 180, SERVOMIN,SERVOMAX);  // map angle of 0 to 180 to Servo min and Servo max 
//   // Serial.print("Angle: ");
//   // Serial.print(ang);
//   // Serial.print(" pulse: ");
//   // Serial.println(pulse);
//   return pulse;
// }