/**
 * 
 * Pull down resistor..
 * 
 * 
 * VCC ---- LED ----  10K RESISTOR ----- Pin 7
 *                  +
 *                  |
 *                  --- Button --- GND
 *                  
 * When the button is activated, it drains the energy and PIN 7
 * gets zero.  Otherwise, Pin7 is connected and gets high.
 * (Pin 7 is inverted, it will light up when the button is not pressed)
 */



int ledPin = 13; // LED connected to digital pin 13
int inPin = 7;   // pushbutton connected to digital pin 7
int val = 0;     // variable to store the read value


void setup()
{
  pinMode(ledPin, OUTPUT);      // sets the digital pin 13 as output
  pinMode(inPin, INPUT);      // sets the digital pin 7 as input
}

void loop()
{
  val = digitalRead(inPin);   // read the input pin
  digitalWrite(ledPin, val);    // sets the LED to the button's value
  delay(50);
}

