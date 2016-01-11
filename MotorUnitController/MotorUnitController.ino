/**
 * Adafruit Shield Motor Controller.
 * 
 * It uses AFMotor.h Adafruit library.
 * 
 * 
 */


#include <AFMotor.h>
#include <Servo.h> 


AF_DCMotor laser(1, MOTOR12_64KHZ);
AF_DCMotor turret(2, MOTOR12_64KHZ);
AF_DCMotor grip(3, MOTOR12_64KHZ);
AF_DCMotor shoulder(4, MOTOR12_64KHZ);

 
Servo myservo;  // create servo object to control a servo 
                // twelve servo objects can be created on most boards
 
int pos = 0;    // variable to store the servo position 


int state=0;

int speeds = 255;

// create motor #2, 64KHz pwm
void setup() {
 Serial.begin(115200); // set up Serial library at 9600 bps
 Serial.println("Motor Unit Neuron");

 //shoulder.setSpeed(255);
 //grip.setSpeed(255);
 turret.setSpeed(255);
 laser.setSpeed(250);

 myservo.attach(9);  // Servo2 orange in
}

int incomingByte = 0;

char buffer[3];

void loop() {

 if (Serial.available() > 0) {
   
    char syncbyte = Serial.read();
   

    if (syncbyte == 'A')
    {   
   
      int readbytes = Serial.readBytes(buffer, 4);
      
      if (readbytes == 4) {
        int action = buffer[0]-48;
        int a = buffer[1]-48;
        int b = buffer[2]-48;
        int c = buffer[3]-48;

        speeds = a*100 + b*10 * c;
        state = action;
      }
    }

 }
 
   
 switch(state)
 {
  case 1: 
    grip.run(FORWARD);
    myservo.write(speeds);
    break;
  case 2:
    grip.run(BACKWARD);
    myservo.write(-speeds);
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
  case 8:
    myservo.attach(9);
    state=0;
    break;
  case 9:
    grip.run(RELEASE); 
    myservo.detach();   
    state=0;
    break;
   default:
    // Do Nothing
    state=0;
    break;
    
 }

 delay(40);

} 
