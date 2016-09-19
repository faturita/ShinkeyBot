/**
 * Motor Unit Controller for ShinkeyBot
 * 
 * It uses AFMotor.h Adafruit library and Shield (v1)
 * 
 * Gripper 1 DC Motor -> M1
 * Shoulder 2 DC Motor 12 V -> M2
 * Tesaki 4 DC Motor del Servo roto 6 V -> M4
 * 
 * Servo Wrist 9V 180 -> Servo 1 Pin 10
 * Servo Elbow 9V 360 -> Servo 2 Pin 9 Coaxial
 */


#include <AFMotor.h>
#include <Servo.h> 

bool debug = true;

// create motor objects, 64KHz pwm
AF_DCMotor grip(1, MOTOR12_64KHZ);
AF_DCMotor tesaki(4, MOTOR12_64KHZ);
AF_DCMotor shoulder(2, MOTOR12_64KHZ);

 
Servo wrist; 
Servo elbow;


int state=0;
int speeds = 255;


void setup() {
 Serial.begin(9600); // set up Serial library at 9600 bps
 Serial.println("Motor Unit Neuron");

 wrist.attach(10);
 elbow.attach(9);

}

int incomingByte = 0;

char buffer[4];

int direction=0;
int pos=48;
int desiredpos = 48;

void update(Servo servo) {

  if (desiredpos != pos)
  {
    //Serial.print(pos);Serial.print("--");
    //Serial.println(desiredpos);
    servo.write(pos);
  
    pos+=direction;
    
    if (pos>=185)
    {
      //Serial.print("Reset down:");
      //Serial.println(counter++);
      direction=-1;
    }
  
    if (pos<=48)
    {
      //Serial.print("Reset up:");
      //Serial.println(counter++);
      direction=1;    
    }
  }

} 

void push(AF_DCMotor motor) {
    motor.run(FORWARD);
    motor.setSpeed(0);
    delay(50);
    motor.setSpeed(255);
    delay(50);  
}

void pull(AF_DCMotor motor) {
    motor.run(BACKWARD);
    motor.setSpeed(0);
    delay(50);
    motor.setSpeed(255);
    delay(250);  
}

int counter;

void loop() {

 if (Serial.available() > 0) {
   
    char syncbyte = Serial.read();

    if (syncbyte == 'I')
    {
      Serial.println("MTRN");
    }

    if (syncbyte == 'D')
    {
      debug = (!debug);
    }

    if (syncbyte == 'A')
    {   
      // Format A1000 >> A1220   --> Close grip
      // A2255 >> Open Grip
      // A6090 >> 90 deg wrist A6010 --> A6180
      // A3220 or A4220 Move forward backward shoulder
      // AA150 -> Keep elbow steady, AA140 backward AA160 forward (AA100 --> AA150 --> AA200)
      // Format A5000  Reset everything.
      int readbytes = Serial.readBytes(buffer, 4);
      
      if (readbytes == 4) {
        Serial.println ( (int)buffer[0] );
        int action = 0;
        if (buffer[0] >= 65)  // send alpha hexa actions.
          action = buffer[0]-65+10;
        else
          action = buffer[0]-48;
        int a = buffer[1]-48;
        int b = buffer[2]-48;
        int c = buffer[3]-48;

        speeds = atoi(buffer+1);
        state = action;

        if (debug) {
          Serial.print("Action:");
          Serial.print(action);
          Serial.print("/");
          Serial.println(speeds);
        }
      }
    }

 }

 // Update the servo wrist position.
 update(wrist);
 
 switch(state)
 {
  case 1: 
    //grip.write(speeds);
    grip.setSpeed(speeds);
    grip.run(FORWARD);
    break;
  case 2:
    //grip.write(-speeds);
    grip.setSpeed(speeds);
    grip.run(BACKWARD);
    break;
  case 3:
    // Go up
    shoulder.setSpeed(speeds);
    shoulder.run(FORWARD);
    break;
  case 4:
    shoulder.setSpeed(speeds);
    shoulder.run(BACKWARD);
    break;
  case 5:
    grip.run(RELEASE);
    tesaki.run(RELEASE);
    elbow.detach();
    state=0;
    break;
  case 6:
    // Update desired position.
    desiredpos=speeds;
    if (pos<desiredpos)
      direction = 1;
    else
      direction =-1;
    break;
  case 8:
    tesaki.setSpeed(speeds);
    tesaki.run(BACKWARD);
    break;
  case 9:
    tesaki.setSpeed(speeds);
    tesaki.run(FORWARD);
    break;
  case 0x0a:
    // 150x10 is no movement. 360 servo.
    elbow.writeMicroseconds(speeds*10);
    counter=0;
    break;
   default:
    // Do Nothing
    state=0;
    break;
    
 }
 counter=counter+1;
 if (counter>=1000) {
  elbow.writeMicroseconds(1500);
  counter=0;
 }

 delay(10);

} 
