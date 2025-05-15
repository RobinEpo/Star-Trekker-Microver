#include "Wire.h"

enum SERVO_SIDE {LEFT = 0x01, RIGHT = 0x02};
enum Direction {FRWRD, BACK};
const byte adress_slave = LEFT;           // Utiliser 0x02 pour le moteur 2 et changer pinouts, sinon même code

const int FrontIN1 =  (adress_slave == LEFT) ? 3   : 11;
const int FrontIN2 =  (adress_slave == LEFT) ? 5   : 10;                     // Moteurs avant et arrière (même côté)
const int CentreIN1 = (adress_slave == LEFT) ? 6   : 9;
const int CentreIN2 = (adress_slave == LEFT) ? 9   : 6;
const int BackIN1 =   (adress_slave == LEFT) ? 10  : 5;
const int BackIN2 =   (adress_slave == LEFT) ? 11  : 3;

//magic numbers
const int length_data = 3;
const int speed_min = 30;
const int speed_max = 240;
//

// bool data_received = false;
int8_t received_data[length_data];
int8_t abs8(int8_t in);

int speed1 = 0, speed2 = 0, speed3 = 0;
Direction direction1 = FRWRD, direction2 = FRWRD, direction3 = FRWRD;

void ClearBuffer();
void receiveEvent(int numBytes);
void AttributeSpeedsDir();
void TransferSpeedsDir();
int8_t abs8(int8_t in);
void write_motor_speed(const int pin_frwd, const int pin_back, int spd, Direction dir);


void setup() 
{
  Serial.begin(9600);
  Wire.begin(adress_slave);  
  Wire.onReceive(receiveEvent);
  pinMode(FrontIN1, OUTPUT);
  pinMode(FrontIN2, OUTPUT);
  pinMode(CentreIN1, OUTPUT);
  pinMode(CentreIN2, OUTPUT);
  pinMode(BackIN1, OUTPUT);
  pinMode(BackIN2, OUTPUT);
  Serial.println("Setted up");
}

void loop() {}

void receiveEvent(int numBytes)
{
  if (numBytes >= length_data)
  {
    for (unsigned i = 0; i < length_data; i++) {
      received_data[i] = (int8_t)(Wire.read());
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
  speed1 = abs8(received_data[0]); // between 0 and 127
  direction1 = (received_data[0] < 0) ? FRWRD : BACK;
  speed1 = 2*speed1 + 1;           // between 1 and 255 

  speed2 = abs8(received_data[1]);
  direction2 = (received_data[1] < 0) ? FRWRD : BACK;
  speed2 = 2*speed2 + 1;    

  speed3 = abs8(received_data[2]); 
  direction3 = (received_data[3] < 0) ? FRWRD : BACK;
  speed3 = 2*speed3 + 1;    
}

void TransferSpeedsDir()
{
  Serial.print("Speeds = ");
  Serial.print(speed1);
  Serial.print(speed2);
  Serial.println(speed3);
  
  write_motor_speed(FrontIN1, FrontIN2, speed1, direction1);
  write_motor_speed(CentreIN1, CentreIN2, speed2, direction2);
  write_motor_speed(BackIN1, BackIN2, speed3, direction3);
}

void write_motor_speed(const int pin_frwd, const int pin_back, int spd, Direction dir)
{
  spd = (spd <= speed_min) ? 0 : spd; 
  spd = (spd >= speed_max) ? 255 : spd;
  if (dir == FRWRD) {
    digitalWrite(pin_back, LOW);
    analogWrite(pin_frwd, spd);
  } else {
    digitalWrite(pin_frwd, LOW);
    analogWrite(pin_back, spd);
  }
}

// QoL functions

int8_t abs8(int8_t in)
{
  if (in == -128) {
    return 127;
  }
  return (in < 0) ? -in : in; 
}