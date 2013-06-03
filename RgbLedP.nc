/**
 * TinyOS implementation of the Grove RGB LED
 **/

#include "Timer.h"

generic module RgbLedP() @safe()
{
  provides interface Init;
  provides interface RgbLed;
  
  uses interface GeneralIO as ClockPin;
  uses interface GeneralIO as DataPin;
}

implementation
{

  void clk() {
    //uint16_t j = 2000;

    // set clock low
    call ClockPin.set();

    // delay
    //while(j--) {}

    // set clock hihg
    call ClockPin.clr();

    // delay
    //j = 2000;
    //while(j--) {} 
  }
  
  /** helper method **/
  void sendByte(uint8_t data) {
  uint8_t i=0;
    // Send one bit at a time, starting with the MSB
    for (i=0; i < 8; i++)
    {
        // If MSB is 1, write one and clock it, else write 0 and clock
        if ((data & 0x80) != 0)
          // write high on data pin
          call DataPin.set();
        else
          // write low on data pin
          call DataPin.clr();
        clk();

        // Advance to the next bit to send
        data <<= 1;
    }
  }

  command error_t Init.init() {
  
    // TODO: insert your code here
    call ClockPin.makeOutput();
    call DataPin.makeOutput();
  
    return SUCCESS;
  }


  command void RgbLed.setColorRgb(uint8_t red, uint8_t green, uint8_t blue) {

    // Start by sending a byte with the format "1 1 /B7 /B6 /G7 /G6 /R7 /R6"
    uint8_t prefix = 0b11000000;

    sendByte(0x00);
    sendByte(0x00);
    sendByte(0x00);
    sendByte(0x00);  
    
    if ((blue & 0x80) == 0)     prefix |= 0b00100000;
    if ((blue & 0x40) == 0)     prefix |= 0b00010000; 
    if ((green & 0x80) == 0)    prefix |= 0b00001000;
    if ((green & 0x40) == 0)    prefix |= 0b00000100;
    if ((red & 0x80) == 0)      prefix |= 0b00000010;
    if ((red & 0x40) == 0)      prefix |= 0b00000001;
    
    // send the prefix
    sendByte(prefix);
        
    // Now must send the 3 colors
    sendByte(blue);
    sendByte(green);
    sendByte(red);

    // chain resend
    sendByte(prefix);

    // send colours
    sendByte(blue);
    sendByte(green);
    sendByte(red);

    sendByte(0x00);
    sendByte(0x00);
    sendByte(0x00);
    sendByte(0x00);

  }

  //function to update the colours on a chain of leds. 
  command void RgbLed.setMultRgb(uint8_t* red, uint8_t* green, uint8_t* blue, uint8_t len) {

    int i;

    //TODO: check if this needs to be done for each of the leds, i.e. if 5 leds do this x 5
    sendByte(0x00);
    sendByte(0x00);
    sendByte(0x00);
    sendByte(0x00); 

    for (i=0; i < len; i++) {

      uint8_t prefix = 0b11000000;

      if ((blue[i] & 0x80) == 0)     prefix |= 0b00100000;
      if ((blue[i] & 0x40) == 0)     prefix |= 0b00010000; 
      if ((green[i] & 0x80) == 0)    prefix |= 0b00001000;
      if ((green[i] & 0x40) == 0)    prefix |= 0b00000100;
      if ((red[i] & 0x80) == 0)      prefix |= 0b00000010;
      if ((red[i] & 0x40) == 0)      prefix |= 0b00000001;

      // chain resend
      sendByte(prefix);

      // send colours
      sendByte(blue[i]);
      sendByte(green[i]);
      sendByte(red[i]);
    }

    sendByte(0x00);
    sendByte(0x00);
    sendByte(0x00);
    sendByte(0x00); 
  }
}

