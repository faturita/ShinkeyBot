/**
 * Adafruit Shield Motor Controller.
 * 
 * It uses AFMotor.h Adafruit library.
 * 
 * 
 */


#include <AFMotor.h>


AF_DCMotor laser(1, MOTOR12_64KHZ);
AF_DCMotor turret(2, MOTOR12_64KHZ);
AF_DCMotor grip(3, MOTOR12_64KHZ);
AF_DCMotor shoulder(4, MOTOR12_64KHZ);


int state=0;

// create motor #2, 64KHz pwm
void setup() {
 Serial.begin(9600); // set up Serial library at 9600 bps
 Serial.println("Motor Unit Neuron");

 shoulder.setSpeed(255);
 grip.setSpeed(255);
 turret.setSpeed(255);
 laser.setSpeed(250);
}

int incomingByte = 0;

void loop() {

 if (Serial.available() > 0) {
    incomingByte = Serial.read();
    
    if (incomingByte == 'a')
    {
      laser.setSpeed(250);
    }

    state = incomingByte-48;
  
 }
 
   
 switch(state)
 {
  case 1: 
    grip.run(FORWARD);
    break;
  case 2:
    grip.run(BACKWARD);
    break;
  case 3:
    shoulder.run(FORWARD);
    break;
  case 4:
    shoulder.run(BACKWARD);
    break;
  case 5:
    shoulder.run(RELEASE);
    state=0;
    break;
  case 9:
    grip.run(RELEASE);    
    state=0;
    break;
  case 6:
    turret.run(FORWARD);
    laser.run(FORWARD);
    break;
  case 7:
    turret.run(BACKWARD);
    laser.run(BACKWARD);
    break;
  case 8:
    turret.run(RELEASE);  
    laser.run(RELEASE);  
    state=0;
    break;
   default:
    // Do Nothing
    state=0;
    break;
    
 }

 delay(400);

} 
