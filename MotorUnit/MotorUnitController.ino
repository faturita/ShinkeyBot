/**
 * Adafruit Shield Motor Controller.
 * 
 * It uses AFMotor.h Adafruit library.
 * 
 * 
 */


#include <AFMotor.h>


AF_DCMotor wheel1(1, MOTOR12_64KHZ);
AF_DCMotor wheel2(2, MOTOR12_64KHZ);
AF_DCMotor grip(3, MOTOR12_64KHZ);
AF_DCMotor shoulder(4, MOTOR12_64KHZ);


int state=0;

// create motor #2, 64KHz pwm
void setup() {
 Serial.begin(9600); // set up Serial library at 9600 bps
 Serial.println("Motor test!");
 
 wheel1.setSpeed(255); // setthe speed to 200/255
 wheel2.setSpeed(255);

 //shoulder.setSpeed(200);
 grip.setSpeed(100);
}


void loop() {
 Serial.print("tick");

 switch(state)
 {
  case 0: 
    wheel1.run(FORWARD);
    wheel2.run(FORWARD);
    grip.run(FORWARD);
    state++;
    break;
  case 1:
    wheel1.run(FORWARD);
    wheel2.run(BACKWARD);
    grip.run(BACKWARD);
    state++;
    break;
  case 2:
    wheel1.run(FORWARD);
    wheel2.run(FORWARD);
    state++;
  case 3:
    wheel1.run(BACKWARD);
    wheel2.run(FORWARD);
    state++;
  case 4:
    wheel1.run(RELEASE); //stopped
    wheel2.run(RELEASE);
    //shoulder.run(RELEASE);
    grip.run(RELEASE);    
    state=0;
 }

 delay(800);

} 
