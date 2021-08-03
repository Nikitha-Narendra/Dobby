#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

#define SERVO_FREQ 50
#define USMIN  750
#define USMAX  2250

const uint8_t servo_tilt = 0;
const uint8_t servo_pan = 2;
const uint8_t servo_us = 4;

const int E1 = 6;
const int E2 = 11;


const int M1 = 7;
const int M2 = 12;

int URECHO = 3;
int URTRIG = 5;


/////Pan and Tilt////////////////////////////////////////////////////////////////////

char range_sweep(uint16_t start, uint16_t ends) {
   uint16_t degree,pulselen;
  char stat = 'p';
  for (degree =start; degree<ends;degree++) {
    if(get_distance() < 30 || stat == 'x')
      break;                                   
   
    pulselen = map(degree, 0, 300, USMIN, USMAX);
    Serial1.print("#2 P");
    Serial1.print(pulselen);
    delay(5);
    Serial1.print("\r");
    degree++;
    stat = Serial.read();
    delay(30);
  }
  Serial.println(degree);
 
  for (degree = degree;degree>start; degree--) {
    if(get_distance()<30 || stat=='x')
      break;
    pulselen = map(degree, 0, 300, USMIN, USMAX);
    Serial1.print("#2 P");
    Serial1.print(pulselen);
    delay(5);
    Serial1.print("\r");
    stat = Serial.read();
    delay(30);
  }
  Serial.println(degree);
  initial();
  return stat;
}

void pan() {
  uint16_t degree = 0;
  char stat = 'p';
  while (degree < 300 && stat != 'x') {
    uint16_t pulselen = map(degree, 0, 300, USMIN, USMAX);
    Serial1.print("#2 P");
    Serial1.print(pulselen);
    delay(5);
    Serial1.print("\r");
    degree++;
    stat = Serial.read();
    delay(30);
  }
  Serial.println(degree);
  initial();
  
}

void tilt() {
  uint16_t degree = Serial.parseInt();
  uint16_t pulselen = map(degree, 0, 180, USMIN, USMAX);
  Serial1.print("#4 P");
  Serial1.print(pulselen);
  delay(5);
  Serial1.print("\r");
  delay(30);
}

void sense(uint16_t degree) {

  uint16_t pulselen = map(degree, 0, 180, USMIN, USMAX);
  Serial1.print("#0 P");
  Serial1.print(pulselen);
  delay(5);
  Serial1.print("\r");
  delay(30);
}


/////motor////////////////////////////////////////////////////////////////////////

void stop_motor(void)
{
  Serial.println('x');
  digitalWrite(E1, 0);
  digitalWrite(M1, LOW);
  digitalWrite(E2, 0);
  digitalWrite(M2, LOW);
}

void left(int Speed)
{
  Serial.println('l');
  analogWrite (E1, Speed);
  digitalWrite(M1, HIGH);
  analogWrite (E2, Speed);
  digitalWrite(M2, HIGH);
}


void right (char Speed)
{
  Serial.println('r');
  analogWrite (E1, Speed);
  digitalWrite(M1, LOW);
  analogWrite (E2, Speed);
  digitalWrite(M2, LOW);
}

void backward(char a)
{
  Serial.println('b');
  analogWrite (E1, a);
  digitalWrite(M1, LOW);
  analogWrite (E2, a);
  digitalWrite(M2, HIGH);
}
void advance(char a)
{
  
  analogWrite (E1, a);
  digitalWrite(M1, HIGH);
  analogWrite (E2, a);
  digitalWrite(M2, LOW);
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////
//US Sensor////////////////////////////////////////////////////////////////////////////////////////////////

unsigned int get_distance()
{
  digitalWrite(URTRIG, LOW);
  digitalWrite(URTRIG, HIGH);
  unsigned int DistanceMeasured = 0;
  unsigned long LowLevelTime = pulseIn(URECHO, LOW) ;

  if (LowLevelTime >= 50000)
  {
    Serial.println("Invalid");
  }

  else
  {
    DistanceMeasured = LowLevelTime / 50;
  }

  return DistanceMeasured;
}
////////////////////////////////////////////////////////////////////////////////////////////////////////////
//Search///////////////////////////////////////////////////////////////////////////////////////////////////

void turn_direction(char side) {
  if (side == 'r') {
    right(100);
    delay(1400);
  }
  else {
    left(100);
    delay(1300);
  }
  stop_motor();

  delay(1000);
}

String avoid_obstacle(char side) {

  uint16_t angle = (side == 'r') ? 0 : 180;
  int limit = 0;
  int flag = 0;
  char opposite = (side == 'r') ? 'l' : 'r';
  stop_motor();
  backward(100);
  delay(1000);
  Serial.print("Turning ");
  Serial.println(side);
  turn_direction(side);

  while (get_distance() < 30) {
    limit = 0;
    sense(angle);
    while (get_distance() < 30 && limit < 35) {
      sense(angle);
      advance(50);
      delay(1000);
      limit++;
      sense(100);
      if (get_distance() < 30)
        flag = 1;
    }

    if (flag == 1) {
      advance(50);
      delay(1000);
      stop_motor();
      delay(500);
      turn_direction(side);
      return "continue";
    }

    if (limit >= 35) {
      return "wall";
    }

    advance(50);
    delay(1000);
    stop_motor();
    delay(500);
    turn_direction(opposite);
    return "continue";

  }

}
void search(char side) {
  Serial.println("Starting search");
  String obstacle = "continue";
  char stat = 's';
  while (stat != 'x') {
    
    Serial.println("Going to opposite wall");
    
    while (get_distance() > 30 && stat != 'x') {
      advance(60);
      Serial.println("Sweeping");
      stat = range_sweep(0,300);
    }


    if (stat != 'x' && obstacle != "wall") {
      backward(100);
      delay(1000);
      stop_motor();

      Serial.print("Turning First ");
      Serial.println(side);
      turn_direction(side);

      Serial.println("Going 4 feet");
      for (int i = 0 ; i < 5 && stat != 'x' ; i++) {
        if (get_distance() < 30) {
          Serial.println("Avoiding Obstacle");
          obstacle = avoid_obstacle(side);

        }
        advance(100);
        delay(1000);
        stat = Serial.read();
      }
      if (obstacle != "wall") {
        Serial.print("Turning second ");
        Serial.println(side);
        turn_direction(side);
      }
      side = (side == 'r') ? 'l' : 'r';
    }
  }
}

void return_home() {
  Serial.println("Returning home");
  char stat = 'h';
  int count = 0;
  unsigned int right_dist = 0;
  unsigned int left_dist = 0;
  char side = 'r';
  advance(100);
  while (stat != 'z') {
    stat = Serial.read();

    if (get_distance() < 30 && stat != 'x') {
      stop_motor();
      sense(0);
      right_dist = get_distance();
      Serial.print(right_dist);
      delay(1000);

      sense(180);
      left_dist = get_distance();
      Serial.print(left_dist);
      delay(1000);

      sense(100);
      char side = (right_dist > left_dist) ? 'l' : 'r';
      avoid_obstacle(side);
      Serial.println('c');
      delay(1000);
      advance(100);
    }
  }
  stop_motor();
}
void initial() {
  stop_motor();

  uint16_t pulselen = map(160, 0, 300, USMIN, USMAX);
    Serial1.print("#2 P");
    Serial1.print(pulselen);
    delay(5);
    Serial1.print("\r");
    delay(100);

  pulselen = map(110, 0, 180, USMIN, USMAX);
  Serial1.print("#0 P");
  Serial1.print(pulselen);
  delay(5);
  Serial1.print("\r");
  delay(100);

  pulselen = map(60, 0, 180, USMIN, USMAX);
  Serial1.print("#4 P");
  Serial1.print(pulselen);
  delay(5);
  Serial1.print("\r");
  delay(100);

}
void setup()
{
  Serial.begin(9600);
  Serial1.begin(115200);
  //motor setup
  for (int i = 3; i < 9; i++)
    pinMode(i, OUTPUT);
  for (int i = 11; i <= 13; i++)
    pinMode(i, OUTPUT);
  digitalWrite(E1, LOW);
  digitalWrite(E2, LOW);
  delay(500);

  //US setup
  pinMode(URTRIG, OUTPUT);
  digitalWrite(URTRIG, HIGH);
  pinMode(URECHO, INPUT);
  delay(500);

  //Pan and Tilt setup
  
}
void loop()
{
  if (Serial.available()) {
    char val = Serial.read();
    Serial.println(val);

    switch (val)
    {
      case 'f': advance(50);
        break;

      case 'b': backward(100);
        break;

      case 'l': left(70);
        break;

      case 'r': right (70);
        break;

      case 'p': pan();
        break;

      case 't': tilt();
        break;

      case 's': sense(60);
        break;

      case 'i': initial();
        break;

      case 'x': stop_motor();
        break;

      case 'h': return_home();
        break;

      case 'u': Serial.println(get_distance());
        break;

      case 'q': Serial.println(get_distance());
        sense(0);
        delay(1000);
        unsigned int right_distance = get_distance();
        delay(1000);


        sense(180);
        delay(1000);
        unsigned int left_distance = get_distance();
        delay(1000);

        sense(100);
        Serial.println(right_distance);
        Serial.println(left_distance);

        char side = (right_distance > left_distance) ? 'r' : 'l';
        search(side);
        break;
    }

  }

}
