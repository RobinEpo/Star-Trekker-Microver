#include "Wire.h"

enum SERVO_SIDE {LEFT = 0x01, RIGHT = 0x02};
const byte adress_slave1 = LEFT;           // Utiliser 0x02 pour le moteur 2 et changer pinouts, sinon même code


const int FrontIN1 =  (adress_slave1 == LEFT) ? 3   : 11;
const int FrontIN2 =  (adress_slave1 == LEFT) ? 5   : 10;                     // Moteurs avant et arrière (même côté)
const int CentreIN1 = (adress_slave1 == LEFT) ? 6   : 9;
const int CentreIN2 = (adress_slave1 == LEFT) ? 9   : 6;
const int BackIN1 =   (adress_slave1 == LEFT) ? 10  : 5;
const int BackIN2 =   (adress_slave1 == LEFT) ? 11  : 3;

const int length_data = 3;
// bool data_received = false;
int8_t received_data[length_data];
int8_t abs8(int8_t in);

int speed1 = 0;                           // Valeur de 0 à 255 pour la vitesse des moteur
bool direction1 = 0;                        // 0 pour l'avant et 1 pour l'arrière

int speed2 = 0;                           // Valeur de 0 à 255 pour la vitesse des moteur
bool direction2 = 0;                        // 0 pour l'avant et 1 pour l'arrière

// Inutile pour l'instant mais sera utile si on utilise 1 driver par moteur
int speed3 = 0;                           // Valeur de 0 à 255 pour la vitesse des moteur
bool direction3 = 0;                        // 0 pour l'avant et 1 pour l'arrière

void ClearBuffer()
{
  while (Wire.available())
  {
    Wire.read();
  }
}

void receiveEvent(int numBytes)
{
  if (numBytes >= length_data)
  {
    for (unsigned i = 0; i < length_data; i++) {
      received_data[i] = (int8_t)(Wire.read() - (byte)128);
    }
    //DEBUG
    for (unsigned i = 0; i < length_data; i++) {
      Serial.println(received_data[i]);
    }
    // ClearBuffer(); //safety net
  
    AttributeSpeedsDir();
    TransferSpeedsDir();
  }
}

void AttributeSpeedsDir()
{
  speed1 = abs8(received_data[0]);
  direction1 = received_data[0] < 0;
  if (speed1 == 128)
  {
    speed1--;
  }
  speed1 *= 2;    // Avoir une plage de 0 à 254

  speed2 = abs8(received_data[1]);
  direction2 = received_data[1] < 0;
  if (speed2 == 128)
  {
    speed2--;
  }
  speed2 *= 2;    // Avoir une plage de 0 à 254

  speed3 = abs8(received_data[2]);
  direction3 = received_data[2] < 0;
  if (speed3 == 128)
  {
    speed3--;
  }
  speed3 *= 2;    // Avoir une plage de 0 à 254
}



void TransferSpeedsDir()
{
  Serial.print("Speeds = ");
  Serial.print(speed1);
  Serial.print(speed2);
  Serial.println(speed3);
  if (speed1 <= (int8_t)6)
  {
    digitalWrite(FrontIN1, LOW);
    digitalWrite(FrontIN2, LOW); 
  } 
  else if (direction1 == 0)
  {
    analogWrite(FrontIN1, speed1);
    digitalWrite(FrontIN2, LOW);
  } else {
    digitalWrite(FrontIN1, LOW);
    analogWrite(FrontIN2, speed1);
  }

  if (speed2 <= (int8_t)6)
  {
    digitalWrite(CentreIN1, LOW);
    digitalWrite(CentreIN2, LOW); 
  } 
  else if (direction2 == 0)
  {
    analogWrite(CentreIN1, speed2);
    digitalWrite(CentreIN2, LOW);
  } else {
    digitalWrite(CentreIN1, LOW);
    analogWrite(CentreIN2, speed2);
  }

  if (speed3 <= (int8_t)6)
  {
    digitalWrite(BackIN1, LOW);
    digitalWrite(BackIN2, LOW); 
  } 
  else if (direction3 == 0)
  {
    analogWrite(BackIN1, speed3);
    digitalWrite(BackIN2, LOW);
  } else {
    digitalWrite(BackIN1, LOW);
    analogWrite(BackIN2, speed3);
  }
}



void setup() 
{
  Serial.begin(9600);
  Wire.begin(adress_slave1);  
  Wire.onReceive(receiveEvent);
  pinMode(FrontIN1, OUTPUT);
  pinMode(FrontIN2, OUTPUT);
  pinMode(CentreIN1, OUTPUT);
  pinMode(CentreIN2, OUTPUT);
  pinMode(BackIN1, OUTPUT);
  pinMode(BackIN2, OUTPUT);
  Serial.println("Setted up");
}

void loop() 
{}


int8_t abs8(int8_t in)
{
  return (in < 0) ? -in : in; 
}
