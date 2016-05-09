/**
 * Motor Unit Controller for ShinkeyBot
 * 
 * It uses AFMotor.h Adafruit library and Shield (v1)
 * 
 * 
 */


#include <AFMotor.h>
#include <Servo.h> 


// create motor objects, 64KHz pwm
//AF_DCMotor laser(1, MOTOR12_64KHZ);
//AF_DCMotor turret(4, MOTOR12_64KHZ);
//AF_DCMotor grip(3, MOTOR12_64KHZ);
AF_DCMotor shoulder(2, MOTOR12_64KHZ);

 
Servo wrist;  // create servo object to control a servo 
                // twelve servo objects can be created on most boards


Servo grip;


int state=0;

int speeds = 255;


void setup() {
 Serial.begin(115200); // set up Serial library at 9600 bps
 Serial.println("Motor Unit Neuron");

 //shoulder.setSpeed(255);
 //grip.setSpeed(255);
 //turret.setSpeed(255);
 //laser.setSpeed(250);

 grip.attach(10);  // Servo2 orange in

 wrist.attach(9);

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

void loop() {

 if (Serial.available() > 0) {
   
    char syncbyte = Serial.read();

    if (syncbyte == 'I')
    {
      Serial.println("MTRN");
    }

    if (syncbyte == 'A')
    {   
   
      int readbytes = Serial.readBytes(buffer, 4);
      
      if (readbytes == 4) {
        int action = buffer[0]-48;
        int a = buffer[1]-48;
        int b = buffer[2]-48;
        int c = buffer[3]-48;

        speeds = atoi(buffer+1);
        state = action;

        Serial.print("Speed:");Serial.println(action);
        Serial.println(speeds);
      }
    }

 }
 

 update(wrist);
 
 switch(state)
 {
  case 1: 
    grip.write(speeds);
    break;
  case 2:
    grip.write(-speeds);
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
    shoulder.run(RELEASE);
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
    grip.attach(10);
    wrist.attach(9);
    state=0;
    break;
  case 9:
    grip.detach();   
    wrist.detach();
    state=0;
    break;
   default:
    // Do Nothing
    state=0;
    break;
    
 }

 delay(10);

} 
