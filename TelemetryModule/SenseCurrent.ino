int mVperAmp = 100; // use 185 for 5A, 100 for 20A (I have 2 of that) Module and 66 for 30A Module
double ACSoffset = 2487;

float r1=28600;//32000.0;
//float r1=90900.0;  // this is the first resistance 
float r2=10100.0;  // this is the second resistance to A0

void senseCurrentAndVoltage()
{
  // read the input on analog pin 0:
  int sensorValue = analogRead(A0);
  // Convert the analog reading (which goes from 0 - 1023) to a voltage (0 - 5V):
  float input_voltage = sensorValue * (5.0 / 1023.0);
  float voltage = input_voltage / (r2/(r1+r2)); // 10:1 relation to measure 50V
  //float voltage = input_voltage;

  int currentValue = analogRead(A1);
  double Voltage = (currentValue / 1023.0) * 5000; // Gets you mV
  double Amps = ((Voltage - ACSoffset) / mVperAmp);

  sensor.current = Amps;
  sensor.voltage = voltage;

  
  // print out the value you read:
  if (debug)
  {
    Serial.print(currentValue);
    Serial.print("-");
    Serial.print(voltage,4);
    Serial.print("-");
    Serial.println(Amps,3); // the '3' after voltage allows you to display 3 digits after decimal point
  }
}

