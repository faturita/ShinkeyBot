/**
 * \par Copyright (C), 2012-2016, MakeBlock
 * @file    InfraredReceiverTest.ino
 * @author  MakeBlock
 * @version V1.0.0
 * @date    2015/09/01
 * @brief   Description: this file is sample code for Me Infrared Receiver device.
 *
 * Function List:
 * 1. void MeInfraredReceiver::begin(void)
 * 2. int16_t MeInfraredReceiver::read(void)
 * 3. int16_t MeInfraredReceiver::available(void)
 * 4. bool MeInfraredReceiver::buttonState(void)
 * 
 * GND, and VCC to 5V
 * A2 to RX
 * A3 to DAT
 *
 * \par History:
 * <pre>
 * <Author>     <Time>        <Version>      <Descr>
 * Mark Yan     2015/09/01    1.0.0          rebuild the old lib
 * </pre>
 */
#include "MeOrion.h"
#include <SoftwareSerial.h>

MeInfraredReceiver infraredReceiverDecode(PORT_3);

void setupir()
{
  infraredReceiverDecode.begin();
  Serial.begin(9600);
  Serial.println("InfraredReceiverDecode Start!");
}

int getcommand()
{
  uint8_t ReceiverCode;
  uint8_t buttonState;
  static uint8_t PrebuttonState = 0;

  buttonState = infraredReceiverDecode.buttonState();
  if(PrebuttonState != buttonState)
  {
    PrebuttonState = buttonState;
    //Serial.print("buttonState 0x");
    //Serial.println(buttonState);
  }
  //Serial.println("Checking...");
  if(infraredReceiverDecode.available())
  {
    ReceiverCode = infraredReceiverDecode.read();
    //Serial.print(ReceiverCode);
    switch(ReceiverCode)
    {
       case IR_BUTTON_A: //Serial.println("Press A."); 
       return '+';
       break;
       case IR_BUTTON_B: //Serial.println("Press B."); 
       return '-';
       break;
       case IR_BUTTON_C: Serial.println("Press C."); break;
       case IR_BUTTON_D: Serial.println("Press D."); break;
       case IR_BUTTON_E: //Serial.println("Press E."); 
       return 'L';
       break;
       case IR_BUTTON_F: //Serial.println("Press F."); 
       return 'l';
       break;
       case IR_BUTTON_SETTING: //Serial.println("Press Setting."); 
       return 'E';
       break;
       case IR_BUTTON_UP: //Serial.println("Press Up."); 
       return '2';break;
       case IR_BUTTON_DOWN: //Serial.println("Press Down."); 
       return '3';
       break;
       case IR_BUTTON_LEFT: //Serial.println("Press Left."); 
       return '5';
       break;
       case IR_BUTTON_RIGHT: //Serial.println("Press Right."); 
       return '4';
       break;
       case IR_BUTTON_0: //Serial.println("Press 0."); 
       return '9';
       break;
       case IR_BUTTON_1: Serial.println("Press 1."); break;
       case IR_BUTTON_2: Serial.println("Press 2."); break;
       case IR_BUTTON_3: Serial.println("Press 3."); break;
       case IR_BUTTON_4: Serial.println("Press 4."); break;
       case IR_BUTTON_5: Serial.println("Press 5."); break;
       case IR_BUTTON_6: Serial.println("Press 6."); break;
       case IR_BUTTON_7: Serial.println("Press 7."); break;
       case IR_BUTTON_8: Serial.println("Press 8."); break;
       case IR_BUTTON_9: Serial.println("Press 9."); break;
       default: break;
    }
  }

  return 0;
}

